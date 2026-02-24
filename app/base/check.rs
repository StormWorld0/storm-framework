// MIT License.
// Copyright (c) 2026 Storm Framework

// See LICENSE file in the project root for full license information.

use sha2::{Sha256, Digest};
use std::fs;
use std::io::{self, Write};
use std::collections::{BTreeMap, HashSet};
use std::path::Path;
use walkdir::WalkDir;
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

fn calculate_hash(path: &Path) -> io::Result<String> {
    let mut file = fs::File::open(path)?;
    let mut hasher = Sha256::new();
    io::copy(&mut file, &mut hasher)?;
    Ok(format!("{:x}", hasher.finalize()))
}

fn main() {
    let db_path = "lib/core/database/signed_manifest.json";
    let env_path = ".env";

    // --- 1. Ambil Public Key dari .env ---
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

    // Kupas header jika perlu
    let mut key_bytes = [0u8; 32];
    let start = if pub_key_full.len() > 32 { pub_key_full.len() - 32 } else { 0 };
    key_bytes.copy_from_slice(&pub_key_full[start..]);

    let public_key = VerifyingKey::from_bytes(&key_bytes).expect("[-] Failed to create VerifyingKey");

    // --- 2. Load & Parse JSON ---
    let content = fs::read_to_string(db_path).expect("[-] ERROR: Manifest file not found");
    let manifest: Manifest = serde_json::from_str(&content).expect("[-] ERROR: JSON format broken");

    // --- 3. Verifikasi Signature ---
    let files_json = serde_json::to_string(&manifest.files).expect("[-] Failed to reserialize");
    let signature_bytes = general_purpose::STANDARD.decode(&manifest.metadata.signature).expect("[-] Invalid Signature Base64");
    let signature = Signature::from_slice(&signature_bytes).expect("[-] Invalid Signature format");

    if public_key.verify(files_json.as_bytes(), &signature).is_err() {
        println!("\n[!] FATAL ERROR: DIGITAL SIGNATURE MISMATCH!");
        std::process::exit(1);
    }

    println!("[+] Digital Signature Verified. Manifest is authentic.");

    // --- 4. Audit Files ---
    let mut verified_count = 0;
    let mut modified_files = Vec::new();
    let mut untracked_files = Vec::new();
    let mut found_in_disk = HashSet::new();

    let ignored_items = [".git", "__pycache__", ".pytest_cache", ".github", "storm.db", "signed_manifest.json", ".gitignore", ".env", "target", "res"];

    for entry in WalkDir::new(".").into_iter().filter_map(|e| e.ok()) {
        let path = entry.path();
        if path.is_file() {
            let path_str = path.to_str().unwrap_or("");
            let mut should_ignore = false;

            for comp in path.components() {
                let name = comp.as_os_str().to_string_lossy();

                for ignored in &ignored_items {
                    if name == *ignored {should_ignore = true; break;}
                }
                if should_ignore {break;}
            }
            if should_ignore {continue;}

            let clean_path = path_str.strip_prefix("./").unwrap_or(path_str);
            found_in_disk.insert(clean_path.to_string());

            match manifest.files.get(clean_path) {
                Some(info) => {
                    if calculate_hash(path).unwrap_or_default() == info.sha256 {
                        verified_count += 1;
                    } else {
                        modified_files.push(clean_path.to_string());
                    }
                }
                None => { untracked_files.push(clean_path.to_string()); }
            }
            print!("\r\x1b[K[*] Verified: {} | Modified: {} | Untracked: {}", verified_count, modified_files.len(), untracked_files.len());
            io::stdout().flush().unwrap();
        }
    }

    // Cek file yang hilang
    let mut missing_files = Vec::new();
    for json_path in manifest.files.keys() {
        if !found_in_disk.contains(json_path) {
            missing_files.push(json_path);
        }
    }

    if !modified_files.is_empty() || !missing_files.is_empty() || !untracked_files.is_empty() {
        println!("\n\n[!] INTEGRITY BREACH DETECTED!");
        for f in &modified_files { println!("    [MODIFIED]  -> {}", f); }
        for f in &missing_files { println!("    [MISSING]  -> {}", f); }
        for f in &untracked_files { println!("    [UNTRACKED]  -> {}", f); }

        if !modified_files.is_empty() || !missing_files.is_empty() {
            println!("\nSTATUS: WARNING - Run 'storm update' to re-sign!!");
        } else {
            println!("\nSTATUS: CRITICAL - File injection detected.");
            std::process::exit(203);
        }
    } else {
        println!("\n\n[✓] System integrity 100% intact.");
    }
}
