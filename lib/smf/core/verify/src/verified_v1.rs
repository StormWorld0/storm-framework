// --- https://github.com/StormWorld0/storm-framework ---
// GPL License.
// Copyright (c) 2026 Storm Framework
// See LICENSE file in the project root for full license information.
// Author: zxelzy

use rayon::prelude::*;
use sha2::{Sha256, Digest};
use std::sync::{mpsc, Arc};
use std::fs::{self, File};
use std::io::{self, BufWriter, Write};
use std::collections::{BTreeMap, HashSet};
use std::path::Path;
use walkdir::{WalkDir, DirEntry};
use serde::{Deserialize, Serialize};
use ed25519_dalek::{VerifyingKey, Signature, Verifier};
use base64::{engine::general_purpose, Engine as _};

#[derive(Serialize, Deserialize, Debug)]
struct Manifest {
    metadata: Metadata,
    files: BTreeMap<String, FileInfo>,
}

#[derive(Serialize, Deserialize, Debug)]
struct Metadata {
    version: String,
    signature: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct FileInfo {
    sha256: String,
    size_bytes: u64,
}

enum VerifyResult {
    Verified(String),
    Modified(String),
    Untracked(String),
}

fn calculate_hash(path: &Path) -> io::Result<String> {
    let mut file = fs::File::open(path)?;
    let mut hasher = Sha256::new();
    io::copy(&mut file, &mut hasher)?;
    Ok(format!("{:x}", hasher.finalize()))
}

// Fungsi helper untuk filter WalkDir agar tidak masuk ke folder yang di-ignore
fn is_ignored(entry: &DirEntry, ignored: &HashSet<&str>) -> bool {
    entry.file_name()
        .to_str()
        .map(|s| ignored.contains(s))
        .unwrap_or(false)
}

fn main() {
    let db_path = "lib/core/database/signed_manifest.json";
    let env_path = ".env";

    // --- SETUP & SIGNATURE VERIFICATION ---
    let env_content = fs::read_to_string(env_path).expect("[-] ERROR: .env not found");
    let pub_key_raw = env_content.lines()
        .find(|line| line.starts_with("STORM_PUBKEY="))
        .map(|line| {
            let parts: Vec<&str> = line.splitn(2, '=').collect();
            parts[1].trim()
        })
        .expect("[-] ERROR: STORM_PUBKEY not found");

    let pub_key_clean = pub_key_raw.trim_matches(|c: char| c.is_whitespace() || c == '"' || c == '\'');
    let pub_key_full = general_purpose::STANDARD.decode(pub_key_clean).expect("[-] Invalid Base64 Public Key");

    let mut key_bytes = [0u8; 32];
    let start = if pub_key_full.len() > 32 { pub_key_full.len() - 32 } else { 0 };
    key_bytes.copy_from_slice(&pub_key_full[start..]);

    let public_key = VerifyingKey::from_bytes(&key_bytes).expect("[-] Failed to create VerifyingKey");

    let content = fs::read_to_string(db_path).expect("[-] ERROR: Manifest file not found");
    let manifest: Manifest = serde_json::from_str(&content).expect("[-] ERROR: JSON format broken");

    let files_json = serde_json::to_string(&manifest.files).expect("[-] Failed to reserialize");
    let signature_bytes = general_purpose::STANDARD.decode(&manifest.metadata.signature).expect("[-] Invalid Signature Base64");
    let signature = Signature::from_slice(&signature_bytes).expect("[-] Invalid Signature format");

    if public_key.verify(files_json.as_bytes(), &signature).is_err() {
        println!("\n[!] FATAL ERROR: DIGITAL SIGNATURE MISMATCH!");
        std::process::exit(1);
    }
    
    // --- I/O BOUND (Filter Files with Directory Pruning) ---
    let ignored_items: HashSet<&str> = [
        ".git", "__pycache__", ".pytest_cache", ".github", 
        "sqlite", "signed_manifest.json", ".gitignore", 
        ".env", "target", "res", "cache", ".DS_Store", 
        "Thumbs.db", "desktop.ini", ".Spotlight-V100",
        ".Trashes"
    ].into_iter().collect();

    let mut target_files = Vec::new();

    // Pruning at the entry level. WalkDir will not read the contents of ignored folders.
    let walker = WalkDir::new(".").into_iter().filter_entry(|e| !is_ignored(e, &ignored_items));

    for entry in walker.filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_file() {
            let path_str = path.to_str().unwrap_or("");
            let clean_path = path_str.strip_prefix("./").unwrap_or(path_str).to_string();
            target_files.push((path.to_path_buf(), clean_path));
        }
    }

    // --- MULTITHREADING HASHING & REALTIME UI ---
    let mut verified_count = 0;
    let mut modified_files = Vec::new();
    let mut untracked_files = Vec::new();
    let mut found_in_disk = HashSet::with_capacity(target_files.len());

    let (tx, rx) = mpsc::channel();

    // Wrap manifest.files with Arc (main memory allocation)
    let manifest_files = Arc::new(manifest.files);
    
    // Create a duplicate pointer to hand to the worker thread.
    let manifest_files_worker = Arc::clone(&manifest_files); 

    std::thread::spawn(move || {
        target_files.into_par_iter().for_each_with(tx, |sender, (path_buf, clean_path)| {
            
            // Use manifest_files_worker in this parallel thread
            let result = match manifest_files_worker.get(&clean_path) {
                Some(info) => {
                    let calculated_hash = calculate_hash(&path_buf).unwrap_or_default();
                    if calculated_hash == info.sha256 {
                        VerifyResult::Verified(clean_path)
                    } else {
                        VerifyResult::Modified(clean_path)
                    }
                }
                None => VerifyResult::Untracked(clean_path),
            };
            let _ = sender.send(result);
        });
    });

    // The main thread executes the UI loop smoothly.
    while let Ok(message) = rx.recv() {
        // Kumpulkan state secara silent (tanpa mencetak angka)
        match message {
            VerifyResult::Verified(path) => {
                verified_count += 1;
                found_in_disk.insert(path);
            }
            VerifyResult::Modified(path) => {
                modified_files.push(path.clone());
                found_in_disk.insert(path);
            }
            VerifyResult::Untracked(path) => {
                untracked_files.push(path);
            }
        }
    }

    // Path to cache state injection
    let inj_path = "lib/smf/core/sf/cache/integrity/injection.state";

    if !untracked_files.is_empty() {
        let path_obj = Path::new(inj_path);
        if let Some(parent) = path_obj.parent() {
            if !parent.exists() {
                if let Err(e) = fs::create_dir_all(parent) {
                    eprintln!("I/O Error: Failed to create directory hierarchy in '{}': {}", parent.display(), e);
                }
            }
        }
        
        match File::create(path_obj) {
            Ok(file) => {
                let mut writer = BufWriter::new(file);
                let mut write_success = true;

                for untracked in &untracked_files {
                    if let Err(e) = writeln!(writer, "{}", untracked) {
                        eprintln!("I/O Error writing string to buffer: {}", e);
                        write_success = false;
                        break;
                    }
                }
                if write_success {
                    if let Err(e) = writer.flush() {
                        eprintln!("I/O Error flushing disk: {}", e);
                    }
                }
            }
            Err(e) => {
                eprintln!("Failed to create/open file at path '{}': {}", path_obj.display(), e);
            }
        }
    }
    
    // --- IDENTIFICATION OF MISSING FILES ---
    // The main thread still has access via the original manifest_files
    let missing_files: Vec<String> = manifest_files.keys()
        .filter(|json_path| !found_in_disk.contains(*json_path))
        .cloned()
        .collect();

    if !modified_files.is_empty() || !missing_files.is_empty() || !untracked_files.is_empty() {
        println!("\n\n[!] INTEGRITY BREACH DETECTED [!]");
        for f in &modified_files { println!("    [MODIFIED]  -> {}", f); }
        for f in &missing_files { println!("    [MISSING]   -> {}", f); }
        for f in &untracked_files { println!("    [INJECTION] -> {}", f); }

        // Threat vector extraction into boolean flags
        let has_injection = !untracked_files.is_empty();
        let has_tampering = !modified_files.is_empty() || !missing_files.is_empty();

        // Exclusive evaluation of the severity matrix (Severity Matrix)
        match (has_injection, has_tampering) {
            (true, true) => {
                // Priority 1: Compound Threat (Injection + Modification/Loss)
                println!("\n[*] STATUS: CRITICAL");
                println!("[*] MESSAGE: Compound threat detected (File Injection + Tampering).");
                println!("[*] ACTION:  1. Run (storm --clean) to remove the injected files.");
                println!("             2. Run (storm --update) to re-sign and back to default.");
                std::process::exit(203);
            }
            (true, false) => {
                // Priority 1: Pure Injection
                println!("\n[*] STATUS: CRITICAL");
                println!("[*] MESSAGE: File injection detected.");
                println!("[*] ACTION: Delete the files that injection detects.");
                println!("            Run (storm --clean) to remove the injected files before restarting.");
                std::process::exit(203);
            }
            (false, true) => {
                // Priority 2: Modified or Lost Files
                println!("\n[*] STATUS: WARNING");
                println!("[*] MESSAGE: Integrity mismatch.");
                println!("[*] ACTION: Run (storm --update) to re-sign and back to default.");
                std::process::exit(1);
            }
            (false, false) => {
                unreachable!() 
            }
        }
    }
}
