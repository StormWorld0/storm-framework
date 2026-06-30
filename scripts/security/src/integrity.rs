use rayon::prelude::*;
use pyo3::prelude::*;
use pyo3::types::{PyTuple};
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, HashSet};
use std::fs::{self, File};
use std::io::{self, Write, BufRead, BufReader, Read};
use std::path::{Path, PathBuf};
use walkdir::WalkDir;
use ed25519_dalek::{SigningKey, Signer};
use base64::{Engine as _, engine::general_purpose::STANDARD as b64};
use serde_json::{json, Value};

macro_rules! log {
    ($($arg:tt)*) => {{
        println!($($arg)*);
        let _ = io::stdout().flush();
    }};
}

// Logika kalkulasi SHA256 (I/O streaming dengan buffer 4KB)
fn calculate_sha256(file_path: &Path) -> std::io::Result<String> {
    let file = File::open(file_path)?;
    let mut reader = BufReader::with_capacity(4096, file);
    let mut hasher = Sha256::new();
    let mut buffer = [0; 4096];

    loop {
        let count = reader.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        hasher.update(&buffer[..count]);
    }

    Ok(hex::encode(hasher.finalize()))
}

#[pyfunction]
fn storm_sign(py: Python) -> PyResult<()> {
    log!("[+] Get started with Storm Framework security.");

    // 1. Memanggil objek Python: from rootmap import ROOT
    let rootmap_mod = PyModule::import(py, "rootmap")?;
    let root_py = rootmap_mod.getattr("ROOT")?;
    let root_path_str: String = root_py.call_method0("__str__")?.extract()?;
    let root_path = PathBuf::from(&root_path_str);

    // 2. Parsing .env secara manual (Sesuai logika asli)
    let env_path = ".env";
    let mut priv_key_b64 = None;

    if Path::new(env_path).exists() {
        if let Ok(file) = File::open(&env_path) {
            let reader = BufReader::new(file);
            for line in reader.lines().flatten() {
                if line.starts_with("STORM_PRIVKEY=") {
                    if let Some(key) = line.split('=').nth(1) {
                        priv_key_b64 = Some(key.trim().to_string());
                    }
                    break;
                }
            }
        }
    }

    let priv_key_b64 = match priv_key_b64 {
        Some(k) => k,
        None => {
            log!("[!] ERROR: STORM_PRIVKEY not found in .env. Reinstall storm!");
            return Ok(());
        }
    };

    // 3. Setup Ignore Lists
    let ignored_dirs: HashSet<&str> = [
        ".git", "__pycache__", ".pytest_cache", ".github",
        "sqlite", ".gitignore", ".env", "res", "target",
        "cache",
    ]
    .iter()
    .cloned()
    .collect();

    // 4. Memanggil Context Manager Python: from apps.utility.spin import StormSpin
    let spin_mod = PyModule::import(py, "apps.utility.spin")?;
    let spin_class = spin_mod.getattr("StormSpin")?;
    let spin_instance = spin_class.call0()?;

    // Eksekusi `with StormSpin():` -> memanggil __enter__
    spin_instance.call_method0("__enter__")?;

    // --- MODIFIKASI DIMULAI DI SINI ---
    // Kita bungkus bagian scanning agar GIL aman
    let manifest = py.allow_threads(|| {
        
        // TAHAP 1: FILTERING (I/O Bound)
        // Kumpulkan semua file yang valid secara sekuensial.
        let valid_entries: Vec<_> = WalkDir::new(&root_path)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|entry| {
                let path = entry.path();
                
                // Pastikan ini adalah file
                if !path.is_file() {
                    return false;
                }

                // Abaikan manifest yang sudah ada
                if let Some(filename) = path.file_name().and_then(|n| n.to_str()) {
                    if filename == "signed_manifest.json" {
                        return false;
                    }
                }

                // Cek apakah ada bagian dari path yang masuk ignored_dirs
                for component in path.components() {
                    if let Some(comp_str) = component.as_os_str().to_str() {
                        if ignored_dirs.contains(comp_str) {
                            return false;
                        }
                    }
                }

                true // File valid
            })
            .collect();

        // TAHAP 2: HASHING (CPU Bound)
        // Gunakan Rayon untuk menghitung SHA256 secara multi-thread.
        let root_path_ref = &root_path; // Referensi aman untuk closure Rayon
        
        let manifest_inner: BTreeMap<String, Value> = valid_entries
            .into_par_iter() // Memicu thread pool Rayon
            .filter_map(|entry| {
                let path = entry.path();
                
                if let Ok(relative_path) = path.strip_prefix(root_path_ref) {
                    let rel_path_str = relative_path.to_string_lossy().to_string();
                    
                    // Kalkulasi hashing sekarang berjalan di multi-thread
                    let sha256_hash = calculate_sha256(path).unwrap_or_default();
                    let size_bytes = entry.metadata().map(|m| m.len()).unwrap_or(0);

                    // Kembalikan Tuple (Key, Value) agar bisa dikumpulkan ke BTreeMap
                    Some((
                        rel_path_str,
                        json!({
                            "sha256": sha256_hash,
                            "size_bytes": size_bytes
                        }),
                    ))
                } else {
                    None
                }
            })
            .collect(); // Rayon otomatis melakukan sinkronisasi dan menyusun ulang ke BTreeMap

        manifest_inner
    });
    // --- MODIFIKASI SELESAI ---

    // Eksekusi keluar `with` -> memanggil __exit__
    let none = py.None();
    let args = PyTuple::new(py, &[&none, &none, &none]);
    let _ = spin_instance.call_method1("__exit__", args?);

    // 6. Signing Process
    // Serialisasi BTreeMap ke JSON kompak
    let manifest_string = serde_json::to_string(&manifest)
        .unwrap_or_default()
        .into_bytes();

    // Dekode Base64 & ambil 32 byte terakhir untuk Ed25519
    let priv_bytes = match b64.decode(&priv_key_b64) {
        Ok(b) => b,
        Err(e) => {
            log!("[!] Signing Error (Base64): {}", e);
            return Ok(());
        }
    };

    if priv_bytes.len() < 32 {
        log!("[!] Signing Error: Invalid private key length.");
        return Ok(());
    }

    let mut secret_key_bytes = [0u8; 32];
    secret_key_bytes.copy_from_slice(&priv_bytes[priv_bytes.len() - 32..]);

    let private_key = SigningKey::from_bytes(&secret_key_bytes);
    let signature = private_key.sign(&manifest_string);
    let signature_b64 = b64.encode(signature.to_bytes());

    // 7. Wrap Final Data
    let final_data = json!({
        "metadata": {
            "version": "3.0",
            "signature": signature_b64
        },
        "files": manifest
    });

    // 8. Output file I/O
    let output_dir = root_path.join("lib").join("core").join("database");
    if let Err(e) = fs::create_dir_all(&output_dir) {
        log!("[!] Error creating directories: {}", e);
        return Ok(());
    }

    let manifest_path = output_dir.join("signed_manifest.json");
    if let Err(e) = fs::write(&manifest_path, serde_json::to_string_pretty(&final_data).unwrap()) {
        log!("[!] Error saving manifest: {}", e);
        return Ok(());
    }

    log!("[✓] Success! Manifest signed and saved.");
    Ok(())
}

#[pymodule]
fn libsigned(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(storm_sign, m)?)?;
    Ok(())
}
