# Storm Framework TREE🚀

We will explain the function or use of each folder in the top directory to make it easier to understand each folder.

### apps/

**Objective:**  
Grouping utilities.

**Containing:**  
- Utility Banner.
- Utility Command.
- Utility Base.
- Utility Colors.
- Utility Database.
- Utility Spinner.
- ETC.

**Notes:**  
- Just some logic to help.

---

### assets/

**Objective:**  
Saving static files.

**Containing:**  
- Image
- Wordlist

**Notes:**  
- Safe to save new files except dynamic data.

---

### data/

**Objective:**  
Stores global data and global variables.

**Containing:**  
- OPTIONS variable
- Data Storm

**Notes:**  
- Only to store data globally.

---

### docs/

**Objective:**  
Maintain internal documentation.

**Containing:**  
- Installation
- Module Guide
- ETC.

---

### example/

**Objective:**  
Stores various usage examples.

**Containing:**  
- Logging
- Makefile
- Module
- Metadata
- Plugin
- ETC.

---

### external/

**Objective:**  
Places files outside the internal ecosystem, and is used to store compilation results.

**Containing:**  
- Vendor / Rust Dependencies
- out / Compilation results
- regex / Parsing
- ETC.

**Notes:**  
Only for storing files that are outside the ecosystem or did not previously exist.

---

### internal/

**Objective:**  
Stores files related to the internal ecosystem.

**Containing:**  
- Modules / Binary Modules
- ETC.

**Notes:**  
Not to store unrelated files.

**Rules:**  
- Modules: Must be written in Golang.
- Outside of Modules `internal/source/` You can create new folders as needed.

---

### lib/

**Objective:**  
To store the runtime library.

**Containing:**  
- Roar / Runtime Library.
- Command / Command REPL
- UI
- SQLite Database
- API
- Logging
- Integrity Check
- Cache
- Core
- ETC.

**Notes:**  
You may not modify anything unless it is necessary.

---

### modules/

**Objective:**  
Stores various types of Python modules.

**Containing:**  
- Auxiliary
- Exploit
- ETC.

**Notes:**  
Can include various types of modules.

**Rules:**  
- Python Only
- Complete with metadata.
- Adjust the Options to the module's needs.

---

### plugin/

**Objective:**  
Modifying runtime modules.

**Notes:**  
Free to fill with any plugin.

**Rules:**
- Must be Python
- Must use Class as Entry.
- Include Metadata.

---

### script/

**Objective:**  
To be used in the future.

---

### scripts/

**Objective:**  
Saves the basic logic files for the installation.

**Containing:**  
- Compiler
- Security

---

### tests/

**Objective:**  
Used for testing Storm-Framework to analyze any bugs that may exist.

---


## Storm Framework Structure

TREE.md is the entire structure of the Storm Framework that is `tree -d -I ".git|__pycache__"` for the deepest knowledge of folder & subfolder mapping.

> [!IMPORTANT]
> Updated regularly

```bash
.
├── apps
│   ├── banners
│   ├── base
│   └── utility
├── assets
│   ├── images
│   └── wordlist
│       └── seclists
│           ├── CMS
│           ├── DNS
│           ├── PLS
│           ├── web-content
│           └── web-server
├── data
│   └── option
├── docs
│   └── storm-framework.wiki
├── example
│   ├── logging
│   ├── makefile
│   │   └── hardware_optimization
│   ├── metadata
│   ├── module
│   └── plugin
├── external
│   └── source
│       ├── dep
│       │   └── vendor
│       │       ├── adler2
│       │       │   ├── benches
│       │       │   └── src
│       │       ├── aes
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   ├── armv8
│       │       │   │   ├── ni
│       │       │   │   └── soft
│       │       │   └── tests
│       │       │       └── data
│       │       ├── ahash
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── aho-corasick
│       │       │   └── src
│       │       │       ├── nfa
│       │       │       ├── packed
│       │       │       │   └── teddy
│       │       │       └── util
│       │       ├── arrayref
│       │       │   ├── examples
│       │       │   └── src
│       │       ├── arrayvec
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── autocfg
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── support
│       │       ├── base64
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   ├── engine
│       │       │   │   │   └── general_purpose
│       │       │   │   ├── read
│       │       │   │   └── write
│       │       │   └── tests
│       │       ├── base64ct
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   └── alphabet
│       │       │   └── tests
│       │       │       └── common
│       │       ├── bitflags
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   └── src
│       │       │       ├── external
│       │       │       └── tests
│       │       ├── bitflags-1.3.2
│       │       │   ├── src
│       │       │   └── tests
│       │       │       ├── compile-fail
│       │       │       │   ├── impls
│       │       │       │   ├── non_integer_base
│       │       │       │   └── visibility
│       │       │       └── compile-pass
│       │       │           ├── impls
│       │       │           ├── redefinition
│       │       │           ├── repr
│       │       │           └── visibility
│       │       ├── blake3
│       │       │   ├── benches
│       │       │   ├── c
│       │       │   │   ├── cmake
│       │       │   │   │   └── BLAKE3
│       │       │   │   └── dependencies
│       │       │   │       └── tbb
│       │       │   ├── media
│       │       │   ├── src
│       │       │   └── tools
│       │       ├── block-buffer
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── block-padding
│       │       │   └── src
│       │       ├── bstr
│       │       │   ├── examples
│       │       │   └── src
│       │       │       ├── byteset
│       │       │       └── unicode
│       │       │           └── fsm
│       │       ├── byteorder
│       │       │   ├── benches
│       │       │   └── src
│       │       ├── bzip2
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── bzip2-sys
│       │       │   └── bzip2-1.0.8
│       │       ├── cbc
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── data
│       │       ├── cc
│       │       │   └── src
│       │       │       ├── parallel
│       │       │       └── target
│       │       ├── cfg-if
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── cipher
│       │       │   └── src
│       │       │       └── dev
│       │       ├── const-oid
│       │       │   ├── src
│       │       │   │   └── db
│       │       │   └── tests
│       │       ├── constant_time_eq
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── constant_time_eq-0.1.5
│       │       │   ├── benches
│       │       │   └── src
│       │       ├── cookie
│       │       │   ├── scripts
│       │       │   └── src
│       │       │       └── secure
│       │       ├── cpufeatures
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── cpufeatures-0.2.17
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── crc32fast
│       │       │   ├── benches
│       │       │   └── src
│       │       │       └── specialized
│       │       ├── crossbeam-channel
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   └── flavors
│       │       │   └── tests
│       │       ├── crossbeam-deque
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── crossbeam-epoch
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   └── sync
│       │       │   └── tests
│       │       ├── crossbeam-utils
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   ├── atomic
│       │       │   │   └── sync
│       │       │   └── tests
│       │       ├── crypto-common
│       │       │   └── src
│       │       ├── curve25519-dalek
│       │       │   ├── benches
│       │       │   ├── docs
│       │       │   │   └── assets
│       │       │   ├── src
│       │       │   │   └── backend
│       │       │   │       ├── serial
│       │       │   │       │   ├── curve_models
│       │       │   │       │   ├── fiat_u32
│       │       │   │       │   ├── fiat_u64
│       │       │   │       │   ├── scalar_mul
│       │       │   │       │   ├── u32
│       │       │   │       │   └── u64
│       │       │   │       └── vector
│       │       │   │           ├── avx2
│       │       │   │           ├── ifma
│       │       │   │           └── scalar_mul
│       │       │   ├── tests
│       │       │   └── vendor
│       │       ├── curve25519-dalek-derive
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── der
│       │       │   ├── src
│       │       │   │   ├── asn1
│       │       │   │   │   └── integer
│       │       │   │   ├── reader
│       │       │   │   ├── tag
│       │       │   │   └── writer
│       │       │   └── tests
│       │       │       └── examples
│       │       ├── deranged
│       │       │   └── src
│       │       ├── digest
│       │       │   └── src
│       │       │       ├── core_api
│       │       │       └── dev
│       │       ├── ed25519
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── examples
│       │       ├── ed25519-dalek
│       │       │   ├── benches
│       │       │   ├── docs
│       │       │   │   └── assets
│       │       │   ├── src
│       │       │   │   └── verifying
│       │       │   └── tests
│       │       │       └── examples
│       │       ├── either
│       │       │   └── src
│       │       ├── equivalent
│       │       │   └── src
│       │       ├── fallible-iterator
│       │       │   └── src
│       │       ├── fallible-streaming-iterator
│       │       │   └── src
│       │       ├── fiat-crypto
│       │       │   └── src
│       │       ├── filetime
│       │       │   └── src
│       │       │       └── unix
│       │       ├── find-msvc-tools
│       │       │   └── src
│       │       ├── flate2
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   ├── deflate
│       │       │   │   ├── ffi
│       │       │   │   ├── gz
│       │       │   │   └── zlib
│       │       │   └── tests
│       │       ├── fs_extra
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── fsevent-sys
│       │       │   └── src
│       │       ├── generic-array
│       │       │   └── src
│       │       ├── getrandom
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   └── backends
│       │       │   └── tests
│       │       ├── getrandom-0.2.17
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── common
│       │       ├── globset
│       │       │   ├── benches
│       │       │   └── src
│       │       ├── hashbrown
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   ├── control
│       │       │   │   │   └── group
│       │       │   │   ├── external_trait_impls
│       │       │   │   │   └── rayon
│       │       │   │   └── raw
│       │       │   └── tests
│       │       ├── hashbrown-0.14.5
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   ├── external_trait_impls
│       │       │   │   │   ├── rayon
│       │       │   │   │   └── rkyv
│       │       │   │   └── raw
│       │       │   └── tests
│       │       ├── hashlink
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── heck
│       │       │   └── src
│       │       ├── hex
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── hmac
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── data
│       │       ├── ignore
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── indexmap
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   ├── inner
│       │       │   │   ├── map
│       │       │   │   ├── rayon
│       │       │   │   └── set
│       │       │   └── tests
│       │       ├── indoc
│       │       │   ├── src
│       │       │   └── tests
│       │       │       ├── test_cstr
│       │       │       └── ui
│       │       ├── inotify
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── inotify-sys
│       │       │   └── src
│       │       ├── inout
│       │       │   └── src
│       │       ├── itoa
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── jobserver
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── kqueue
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   └── os
│       │       │   └── tests
│       │       ├── kqueue-sys
│       │       │   └── src
│       │       │       └── constants
│       │       ├── libc
│       │       │   ├── src
│       │       │   │   ├── fuchsia
│       │       │   │   ├── new
│       │       │   │   │   ├── aix
│       │       │   │   │   ├── apple
│       │       │   │   │   │   ├── libc
│       │       │   │   │   │   ├── libpthread
│       │       │   │   │   │   │   ├── pthread_
│       │       │   │   │   │   │   └── sys
│       │       │   │   │   │   │       └── _pthread
│       │       │   │   │   │   └── xnu
│       │       │   │   │   │       ├── arm
│       │       │   │   │   │       ├── i386
│       │       │   │   │   │       ├── mach
│       │       │   │   │   │       │   ├── arm
│       │       │   │   │   │       │   ├── i386
│       │       │   │   │   │       │   └── machine
│       │       │   │   │   │       ├── machine
│       │       │   │   │   │       └── sys
│       │       │   │   │   │           └── _types
│       │       │   │   │   ├── bionic_libc
│       │       │   │   │   │   └── sys
│       │       │   │   │   ├── common
│       │       │   │   │   │   ├── linux_like
│       │       │   │   │   │   └── posix
│       │       │   │   │   ├── cygwin
│       │       │   │   │   ├── dragonfly
│       │       │   │   │   ├── emscripten
│       │       │   │   │   ├── espidf
│       │       │   │   │   ├── freebsd
│       │       │   │   │   │   └── sys
│       │       │   │   │   ├── fuchsia
│       │       │   │   │   ├── glibc
│       │       │   │   │   │   ├── posix
│       │       │   │   │   │   └── sysdeps
│       │       │   │   │   │       ├── nptl
│       │       │   │   │   │       └── unix
│       │       │   │   │   │           └── linux
│       │       │   │   │   │               └── net
│       │       │   │   │   ├── haiku
│       │       │   │   │   ├── hermit_abi
│       │       │   │   │   ├── horizon
│       │       │   │   │   ├── hurd
│       │       │   │   │   ├── illumos
│       │       │   │   │   ├── l4re
│       │       │   │   │   ├── linux_uapi
│       │       │   │   │   │   └── linux
│       │       │   │   │   │       └── can
│       │       │   │   │   ├── musl
│       │       │   │   │   │   ├── arch
│       │       │   │   │   │   │   ├── generic
│       │       │   │   │   │   │   ├── mips
│       │       │   │   │   │   │   │   └── bits
│       │       │   │   │   │   │   └── mips64
│       │       │   │   │   │   │       └── bits
│       │       │   │   │   │   └── sys
│       │       │   │   │   ├── netbsd
│       │       │   │   │   │   ├── net
│       │       │   │   │   │   └── sys
│       │       │   │   │   ├── newlib
│       │       │   │   │   ├── nto
│       │       │   │   │   │   └── net
│       │       │   │   │   ├── nuttx
│       │       │   │   │   ├── openbsd
│       │       │   │   │   │   └── sys
│       │       │   │   │   ├── qurt
│       │       │   │   │   │   └── sys
│       │       │   │   │   ├── redox
│       │       │   │   │   ├── relibc
│       │       │   │   │   ├── rtems
│       │       │   │   │   ├── sgx
│       │       │   │   │   ├── solaris
│       │       │   │   │   ├── solid
│       │       │   │   │   ├── teeos
│       │       │   │   │   ├── trusty
│       │       │   │   │   ├── uclibc
│       │       │   │   │   ├── ucrt
│       │       │   │   │   ├── vita
│       │       │   │   │   ├── vxworks
│       │       │   │   │   ├── wasi
│       │       │   │   │   └── xous
│       │       │   │   ├── qurt
│       │       │   │   ├── solid
│       │       │   │   ├── teeos
│       │       │   │   ├── unix
│       │       │   │   │   ├── aix
│       │       │   │   │   ├── bsd
│       │       │   │   │   │   ├── apple
│       │       │   │   │   │   │   ├── b32
│       │       │   │   │   │   │   └── b64
│       │       │   │   │   │   │       ├── aarch64
│       │       │   │   │   │   │       └── x86_64
│       │       │   │   │   │   ├── freebsdlike
│       │       │   │   │   │   │   ├── dragonfly
│       │       │   │   │   │   │   └── freebsd
│       │       │   │   │   │   │       ├── freebsd11
│       │       │   │   │   │   │       ├── freebsd12
│       │       │   │   │   │   │       ├── freebsd13
│       │       │   │   │   │   │       ├── freebsd14
│       │       │   │   │   │   │       ├── freebsd15
│       │       │   │   │   │   │       └── x86_64
│       │       │   │   │   │   └── netbsdlike
│       │       │   │   │   │       ├── netbsd
│       │       │   │   │   │       └── openbsd
│       │       │   │   │   ├── cygwin
│       │       │   │   │   ├── haiku
│       │       │   │   │   ├── hurd
│       │       │   │   │   ├── linux_like
│       │       │   │   │   │   ├── android
│       │       │   │   │   │   │   ├── b32
│       │       │   │   │   │   │   │   └── x86
│       │       │   │   │   │   │   └── b64
│       │       │   │   │   │   │       ├── aarch64
│       │       │   │   │   │   │       ├── riscv64
│       │       │   │   │   │   │       └── x86_64
│       │       │   │   │   │   ├── emscripten
│       │       │   │   │   │   ├── l4re
│       │       │   │   │   │   │   └── uclibc
│       │       │   │   │   │   │       ├── aarch64
│       │       │   │   │   │   │       └── x86_64
│       │       │   │   │   │   └── linux
│       │       │   │   │   │       ├── arch
│       │       │   │   │   │       │   ├── generic
│       │       │   │   │   │       │   ├── mips
│       │       │   │   │   │       │   ├── powerpc
│       │       │   │   │   │       │   └── sparc
│       │       │   │   │   │       ├── gnu
│       │       │   │   │   │       │   ├── b32
│       │       │   │   │   │       │   │   ├── arm
│       │       │   │   │   │       │   │   ├── csky
│       │       │   │   │   │       │   │   ├── m68k
│       │       │   │   │   │       │   │   ├── mips
│       │       │   │   │   │       │   │   ├── riscv32
│       │       │   │   │   │       │   │   ├── sparc
│       │       │   │   │   │       │   │   └── x86
│       │       │   │   │   │       │   └── b64
│       │       │   │   │   │       │       ├── aarch64
│       │       │   │   │   │       │       ├── loongarch64
│       │       │   │   │   │       │       ├── mips64
│       │       │   │   │   │       │       ├── powerpc64
│       │       │   │   │   │       │       ├── riscv64
│       │       │   │   │   │       │       ├── sparc64
│       │       │   │   │   │       │       └── x86_64
│       │       │   │   │   │       ├── musl
│       │       │   │   │   │       │   ├── b32
│       │       │   │   │   │       │   │   ├── arm
│       │       │   │   │   │       │   │   ├── mips
│       │       │   │   │   │       │   │   ├── riscv32
│       │       │   │   │   │       │   │   └── x86
│       │       │   │   │   │       │   └── b64
│       │       │   │   │   │       │       ├── aarch64
│       │       │   │   │   │       │       ├── loongarch64
│       │       │   │   │   │       │       ├── riscv64
│       │       │   │   │   │       │       ├── wasm32
│       │       │   │   │   │       │       └── x86_64
│       │       │   │   │   │       └── uclibc
│       │       │   │   │   │           ├── arm
│       │       │   │   │   │           ├── mips
│       │       │   │   │   │           │   ├── mips32
│       │       │   │   │   │           │   └── mips64
│       │       │   │   │   │           └── x86_64
│       │       │   │   │   ├── newlib
│       │       │   │   │   │   ├── aarch64
│       │       │   │   │   │   ├── arm
│       │       │   │   │   │   ├── espidf
│       │       │   │   │   │   ├── horizon
│       │       │   │   │   │   ├── powerpc
│       │       │   │   │   │   ├── rtems
│       │       │   │   │   │   └── vita
│       │       │   │   │   ├── nto
│       │       │   │   │   ├── nuttx
│       │       │   │   │   ├── redox
│       │       │   │   │   └── solarish
│       │       │   │   ├── vxworks
│       │       │   │   ├── wasi
│       │       │   │   └── windows
│       │       │   │       ├── gnu
│       │       │   │       └── msvc
│       │       │   └── tests
│       │       ├── libredox
│       │       │   └── src
│       │       ├── libsqlite3-sys
│       │       │   ├── bindgen-bindings
│       │       │   ├── sqlcipher
│       │       │   ├── sqlite3
│       │       │   └── src
│       │       ├── lock_api
│       │       │   └── src
│       │       ├── log
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   └── kv
│       │       │   └── tests
│       │       ├── md-5
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   └── compress
│       │       │   └── tests
│       │       │       └── data
│       │       ├── memchr
│       │       │   └── src
│       │       │       ├── arch
│       │       │       │   ├── aarch64
│       │       │       │   │   └── neon
│       │       │       │   ├── all
│       │       │       │   │   └── packedpair
│       │       │       │   ├── generic
│       │       │       │   ├── wasm32
│       │       │       │   │   └── simd128
│       │       │       │   └── x86_64
│       │       │       │       ├── avx2
│       │       │       │       └── sse2
│       │       │       ├── memmem
│       │       │       └── tests
│       │       │           ├── memchr
│       │       │           └── substring
│       │       ├── memoffset
│       │       │   └── src
│       │       ├── mime
│       │       │   ├── benches
│       │       │   └── src
│       │       ├── mime_guess
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   └── src
│       │       ├── miniz_oxide
│       │       │   └── src
│       │       │       ├── deflate
│       │       │       ├── inflate
│       │       │       └── serde
│       │       ├── mio
│       │       │   ├── examples
│       │       │   └── src
│       │       │       ├── event
│       │       │       ├── net
│       │       │       │   ├── tcp
│       │       │       │   └── uds
│       │       │       └── sys
│       │       │           ├── shell
│       │       │           ├── unix
│       │       │           │   ├── selector
│       │       │           │   └── uds
│       │       │           ├── wasi
│       │       │           └── windows
│       │       ├── notify
│       │       │   └── src
│       │       ├── num-conv
│       │       │   └── src
│       │       ├── once_cell
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── it
│       │       ├── parking_lot
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── parking_lot_core
│       │       │   └── src
│       │       │       └── thread_parker
│       │       │           └── windows
│       │       ├── password-hash
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── pbkdf2
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── data
│       │       ├── pkcs8
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── examples
│       │       ├── pkg-config
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── plain
│       │       │   └── src
│       │       ├── portable-atomic
│       │       │   └── src
│       │       │       ├── gen
│       │       │       ├── imp
│       │       │       │   ├── atomic128
│       │       │       │   ├── atomic64
│       │       │       │   ├── detect
│       │       │       │   ├── fallback
│       │       │       │   ├── float
│       │       │       │   └── interrupt
│       │       │       └── tests
│       │       ├── powerfmt
│       │       │   └── src
│       │       ├── ppv-lite86
│       │       │   └── src
│       │       │       └── x86_64
│       │       ├── proc-macro2
│       │       │   ├── src
│       │       │   │   └── probe
│       │       │   └── tests
│       │       ├── pyo3
│       │       │   ├── assets
│       │       │   ├── emscripten
│       │       │   │   └── emscripten_patches
│       │       │   ├── guide
│       │       │   │   └── src
│       │       │   │       ├── building-and-distribution
│       │       │   │       ├── class
│       │       │   │       ├── conversions
│       │       │   │       ├── ecosystem
│       │       │   │       ├── function
│       │       │   │       └── python-from-rust
│       │       │   ├── pyo3-runtime
│       │       │   │   ├── src
│       │       │   │   │   └── pyo3_runtime
│       │       │   │   └── tests
│       │       │   ├── src
│       │       │   │   ├── conversions
│       │       │   │   │   └── std
│       │       │   │   ├── coroutine
│       │       │   │   ├── err
│       │       │   │   ├── ffi
│       │       │   │   ├── impl_
│       │       │   │   │   └── pyclass
│       │       │   │   ├── inspect
│       │       │   │   ├── pycell
│       │       │   │   ├── pyclass
│       │       │   │   ├── tests
│       │       │   │   │   └── hygiene
│       │       │   │   └── types
│       │       │   └── tests
│       │       ├── pyo3-build-config
│       │       │   └── src
│       │       ├── pyo3-ffi
│       │       │   └── src
│       │       │       └── cpython
│       │       ├── pyo3-macros
│       │       │   └── src
│       │       ├── pyo3-macros-backend
│       │       │   └── src
│       │       │       └── pyfunction
│       │       ├── quote
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── ui
│       │       ├── r-efi
│       │       │   ├── examples
│       │       │   └── src
│       │       │       ├── protocols
│       │       │       └── vendor
│       │       │           └── intel
│       │       ├── rand
│       │       │   └── src
│       │       │       ├── distributions
│       │       │       ├── rngs
│       │       │       │   └── adapter
│       │       │       └── seq
│       │       ├── rand_chacha
│       │       │   └── src
│       │       ├── rand_core
│       │       │   └── src
│       │       ├── rayon
│       │       │   ├── src
│       │       │   │   ├── collections
│       │       │   │   ├── compile_fail
│       │       │   │   ├── iter
│       │       │   │   │   ├── collect
│       │       │   │   │   ├── find_first_last
│       │       │   │   │   └── plumbing
│       │       │   │   └── slice
│       │       │   └── tests
│       │       ├── rayon-core
│       │       │   ├── src
│       │       │   │   ├── broadcast
│       │       │   │   ├── compile_fail
│       │       │   │   ├── join
│       │       │   │   ├── scope
│       │       │   │   ├── sleep
│       │       │   │   ├── spawn
│       │       │   │   └── thread_pool
│       │       │   └── tests
│       │       ├── redox_syscall
│       │       │   └── src
│       │       │       ├── arch
│       │       │       └── io
│       │       ├── redox_syscall-0.5.18
│       │       │   └── src
│       │       │       ├── arch
│       │       │       ├── io
│       │       │       └── scheme
│       │       ├── regex
│       │       │   ├── bench
│       │       │   ├── src
│       │       │   │   ├── regex
│       │       │   │   └── regexset
│       │       │   ├── testdata
│       │       │   └── tests
│       │       ├── regex-automata
│       │       │   ├── src
│       │       │   │   ├── dfa
│       │       │   │   ├── hybrid
│       │       │   │   ├── meta
│       │       │   │   ├── nfa
│       │       │   │   │   └── thompson
│       │       │   │   └── util
│       │       │   │       ├── determinize
│       │       │   │       ├── prefilter
│       │       │   │       └── unicode_data
│       │       │   └── tests
│       │       │       ├── dfa
│       │       │       │   └── onepass
│       │       │       ├── fuzz
│       │       │       ├── gen
│       │       │       │   ├── dense
│       │       │       │   └── sparse
│       │       │       ├── hybrid
│       │       │       ├── meta
│       │       │       └── nfa
│       │       │           └── thompson
│       │       │               ├── backtrack
│       │       │               └── pikevm
│       │       ├── regex-syntax
│       │       │   ├── benches
│       │       │   └── src
│       │       │       ├── ast
│       │       │       ├── hir
│       │       │       └── unicode_tables
│       │       ├── rusqlite
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   │   └── persons
│       │       │   ├── src
│       │       │   │   ├── blob
│       │       │   │   ├── types
│       │       │   │   ├── util
│       │       │   │   └── vtab
│       │       │   └── tests
│       │       ├── rustc_version
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── rustversion
│       │       │   ├── build
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── ui
│       │       ├── ryu
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   ├── buffer
│       │       │   │   └── pretty
│       │       │   └── tests
│       │       │       └── macros
│       │       ├── same-file
│       │       │   ├── examples
│       │       │   └── src
│       │       ├── scopeguard
│       │       │   ├── examples
│       │       │   └── src
│       │       ├── seahash
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── semver
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       │       ├── node
│       │       │       └── util
│       │       ├── serde
│       │       │   └── src
│       │       │       ├── core
│       │       │       │   ├── de
│       │       │       │   ├── private
│       │       │       │   └── ser
│       │       │       └── private
│       │       ├── serde_core
│       │       │   └── src
│       │       │       ├── de
│       │       │       ├── private
│       │       │       └── ser
│       │       ├── serde_derive
│       │       │   └── src
│       │       │       ├── de
│       │       │       └── internals
│       │       ├── serde_json
│       │       │   ├── src
│       │       │   │   ├── io
│       │       │   │   ├── lexical
│       │       │   │   └── value
│       │       │   └── tests
│       │       │       ├── lexical
│       │       │       ├── macros
│       │       │       ├── regression
│       │       │       └── ui
│       │       ├── serde_spanned
│       │       │   └── src
│       │       ├── serde_yaml
│       │       │   ├── src
│       │       │   │   ├── libyaml
│       │       │   │   └── value
│       │       │   └── tests
│       │       ├── sha1
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   └── compress
│       │       │   └── tests
│       │       │       └── data
│       │       ├── sha2
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   ├── sha256
│       │       │   │   └── sha512
│       │       │   └── tests
│       │       │       └── data
│       │       ├── shlex
│       │       │   └── src
│       │       ├── signature
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── simd-adler32
│       │       │   └── src
│       │       │       └── imp
│       │       ├── smallvec
│       │       │   ├── benches
│       │       │   ├── debug_metadata
│       │       │   ├── scripts
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── spki
│       │       │   ├── src
│       │       │   └── tests
│       │       │       └── examples
│       │       ├── subtle
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── syn
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   │   └── gen
│       │       │   └── tests
│       │       │       ├── common
│       │       │       ├── debug
│       │       │       ├── macros
│       │       │       ├── regression
│       │       │       ├── repo
│       │       │       └── snapshot
│       │       ├── target-lexicon
│       │       │   ├── examples
│       │       │   ├── scripts
│       │       │   └── src
│       │       ├── time
│       │       │   ├── benchmarks
│       │       │   ├── src
│       │       │   │   ├── error
│       │       │   │   ├── ext
│       │       │   │   ├── format_description
│       │       │   │   │   ├── parse
│       │       │   │   │   └── well_known
│       │       │   │   │       └── iso8601
│       │       │   │   ├── formatting
│       │       │   │   ├── interop
│       │       │   │   ├── parsing
│       │       │   │   │   └── combinator
│       │       │   │   │       └── rfc
│       │       │   │   ├── serde
│       │       │   │   │   └── timestamp
│       │       │   │   └── sys
│       │       │   │       ├── local_offset_at
│       │       │   │       └── refresh_tz
│       │       │   └── tests
│       │       │       └── integration
│       │       │           ├── compile-fail
│       │       │           └── serde
│       │       ├── time-core
│       │       │   └── src
│       │       ├── time-macros
│       │       │   └── src
│       │       │       ├── format_description
│       │       │       │   └── public
│       │       │       └── helpers
│       │       ├── toml
│       │       │   ├── examples
│       │       │   └── src
│       │       │       └── ser
│       │       │           └── ser_value
│       │       ├── toml_datetime
│       │       │   └── src
│       │       ├── toml_edit
│       │       │   ├── examples
│       │       │   └── src
│       │       │       ├── de
│       │       │       ├── parser
│       │       │       └── ser
│       │       ├── toml_write
│       │       │   └── src
│       │       ├── typenum
│       │       │   ├── src
│       │       │   │   └── gen
│       │       │   └── tests
│       │       ├── unicase
│       │       │   └── src
│       │       │       └── unicode
│       │       ├── unicode-ident
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       │       ├── fst
│       │       │       ├── roaring
│       │       │       ├── tables
│       │       │       └── trie
│       │       ├── unindent
│       │       │   └── src
│       │       ├── unsafe-libyaml
│       │       │   ├── src
│       │       │   │   └── bin
│       │       │   │       └── cstr
│       │       │   └── tests
│       │       │       ├── bin
│       │       │       └── ignorelist
│       │       ├── vcpkg
│       │       │   ├── src
│       │       │   ├── test-data
│       │       │   │   ├── multiline-description
│       │       │   │   │   └── installed
│       │       │   │   │       └── vcpkg
│       │       │   │   │           ├── info
│       │       │   │   │           └── updates
│       │       │   │   ├── no-status
│       │       │   │   │   └── installed
│       │       │   │   │       ├── vcpkg
│       │       │   │   │       │   ├── info
│       │       │   │   │       │   └── updates
│       │       │   │   │       └── x64-windows
│       │       │   │   │           ├── bin
│       │       │   │   │           ├── lib
│       │       │   │   │           │   └── manual-link
│       │       │   │   │           └── tools
│       │       │   │   │               └── openssl
│       │       │   │   └── normalized
│       │       │   │       └── installed
│       │       │   │           ├── arm64-ios
│       │       │   │           │   └── lib
│       │       │   │           ├── vcpkg
│       │       │   │           │   ├── info
│       │       │   │           │   └── updates
│       │       │   │           ├── x64-osx
│       │       │   │           │   └── lib
│       │       │   │           ├── x64-windows
│       │       │   │           │   ├── bin
│       │       │   │           │   ├── debug
│       │       │   │           │   │   ├── bin
│       │       │   │           │   │   └── lib
│       │       │   │           │   │       └── manual-link
│       │       │   │           │   ├── lib
│       │       │   │           │   │   └── manual-link
│       │       │   │           │   └── tools
│       │       │   │           │       └── openssl
│       │       │   │           ├── x64-windows-static
│       │       │   │           │   ├── debug
│       │       │   │           │   │   └── lib
│       │       │   │           │   │       └── manual-link
│       │       │   │           │   └── lib
│       │       │   │           │       └── manual-link
│       │       │   │           └── x86-windows
│       │       │   │               ├── bin
│       │       │   │               └── lib
│       │       │   └── tests
│       │       ├── version_check
│       │       │   └── src
│       │       ├── walkdir
│       │       │   ├── compare
│       │       │   └── src
│       │       │       └── tests
│       │       ├── wasi
│       │       │   └── src
│       │       ├── wasip2
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   └── ext
│       │       │   └── wit
│       │       │       └── deps
│       │       ├── winapi-util
│       │       │   └── src
│       │       ├── windows-link
│       │       │   └── src
│       │       ├── windows-sys
│       │       │   └── src
│       │       │       ├── Windows
│       │       │       │   ├── Wdk
│       │       │       │   │   ├── Devices
│       │       │       │   │   │   ├── Bluetooth
│       │       │       │   │   │   └── HumanInterfaceDevice
│       │       │       │   │   ├── Foundation
│       │       │       │   │   ├── Graphics
│       │       │       │   │   │   └── Direct3D
│       │       │       │   │   ├── NetworkManagement
│       │       │       │   │   │   ├── Ndis
│       │       │       │   │   │   └── WindowsFilteringPlatform
│       │       │       │   │   ├── Storage
│       │       │       │   │   │   └── FileSystem
│       │       │       │   │   │       └── Minifilters
│       │       │       │   │   └── System
│       │       │       │   │       ├── IO
│       │       │       │   │       ├── Memory
│       │       │       │   │       ├── OfflineRegistry
│       │       │       │   │       ├── Registry
│       │       │       │   │       ├── SystemInformation
│       │       │       │   │       ├── SystemServices
│       │       │       │   │       └── Threading
│       │       │       │   └── Win32
│       │       │       │       ├── Data
│       │       │       │       │   ├── HtmlHelp
│       │       │       │       │   └── RightsManagement
│       │       │       │       ├── Devices
│       │       │       │       │   ├── AllJoyn
│       │       │       │       │   ├── Beep
│       │       │       │       │   ├── BiometricFramework
│       │       │       │       │   ├── Bluetooth
│       │       │       │       │   ├── Cdrom
│       │       │       │       │   ├── Communication
│       │       │       │       │   ├── DeviceAndDriverInstallation
│       │       │       │       │   ├── DeviceQuery
│       │       │       │       │   ├── Display
│       │       │       │       │   ├── Dvd
│       │       │       │       │   ├── Enumeration
│       │       │       │       │   │   └── Pnp
│       │       │       │       │   ├── Fax
│       │       │       │       │   ├── HumanInterfaceDevice
│       │       │       │       │   ├── Nfc
│       │       │       │       │   ├── Nfp
│       │       │       │       │   ├── PortableDevices
│       │       │       │       │   ├── Properties
│       │       │       │       │   ├── Pwm
│       │       │       │       │   ├── Sensors
│       │       │       │       │   ├── SerialCommunication
│       │       │       │       │   ├── Tapi
│       │       │       │       │   ├── Usb
│       │       │       │       │   └── WebServicesOnDevices
│       │       │       │       ├── Foundation
│       │       │       │       ├── Gaming
│       │       │       │       ├── Globalization
│       │       │       │       ├── Graphics
│       │       │       │       │   ├── Dwm
│       │       │       │       │   ├── Gdi
│       │       │       │       │   ├── GdiPlus
│       │       │       │       │   ├── Hlsl
│       │       │       │       │   ├── OpenGL
│       │       │       │       │   └── Printing
│       │       │       │       │       └── PrintTicket
│       │       │       │       ├── Management
│       │       │       │       │   └── MobileDeviceManagementRegistration
│       │       │       │       ├── Media
│       │       │       │       │   ├── Audio
│       │       │       │       │   ├── DxMediaObjects
│       │       │       │       │   ├── KernelStreaming
│       │       │       │       │   ├── Multimedia
│       │       │       │       │   ├── Streaming
│       │       │       │       │   └── WindowsMediaFormat
│       │       │       │       ├── NetworkManagement
│       │       │       │       │   ├── Dhcp
│       │       │       │       │   ├── Dns
│       │       │       │       │   ├── InternetConnectionWizard
│       │       │       │       │   ├── IpHelper
│       │       │       │       │   ├── Multicast
│       │       │       │       │   ├── Ndis
│       │       │       │       │   ├── NetBios
│       │       │       │       │   ├── NetManagement
│       │       │       │       │   ├── NetShell
│       │       │       │       │   ├── NetworkDiagnosticsFramework
│       │       │       │       │   ├── P2P
│       │       │       │       │   ├── QoS
│       │       │       │       │   ├── Rras
│       │       │       │       │   ├── Snmp
│       │       │       │       │   ├── WNet
│       │       │       │       │   ├── WebDav
│       │       │       │       │   ├── WiFi
│       │       │       │       │   ├── WindowsConnectionManager
│       │       │       │       │   ├── WindowsFilteringPlatform
│       │       │       │       │   ├── WindowsFirewall
│       │       │       │       │   └── WindowsNetworkVirtualization
│       │       │       │       ├── Networking
│       │       │       │       │   ├── ActiveDirectory
│       │       │       │       │   ├── Clustering
│       │       │       │       │   ├── HttpServer
│       │       │       │       │   ├── Ldap
│       │       │       │       │   ├── WebSocket
│       │       │       │       │   ├── WinHttp
│       │       │       │       │   ├── WinInet
│       │       │       │       │   ├── WinSock
│       │       │       │       │   └── WindowsWebServices
│       │       │       │       ├── Security
│       │       │       │       │   ├── AppLocker
│       │       │       │       │   ├── Authentication
│       │       │       │       │   │   └── Identity
│       │       │       │       │   ├── Authorization
│       │       │       │       │   ├── Credentials
│       │       │       │       │   ├── Cryptography
│       │       │       │       │   │   ├── Catalog
│       │       │       │       │   │   ├── Certificates
│       │       │       │       │   │   ├── Sip
│       │       │       │       │   │   └── UI
│       │       │       │       │   ├── DiagnosticDataQuery
│       │       │       │       │   ├── DirectoryServices
│       │       │       │       │   ├── EnterpriseData
│       │       │       │       │   ├── ExtensibleAuthenticationProtocol
│       │       │       │       │   ├── Isolation
│       │       │       │       │   ├── LicenseProtection
│       │       │       │       │   ├── NetworkAccessProtection
│       │       │       │       │   ├── WinTrust
│       │       │       │       │   └── WinWlx
│       │       │       │       ├── Storage
│       │       │       │       │   ├── Cabinets
│       │       │       │       │   ├── CloudFilters
│       │       │       │       │   ├── Compression
│       │       │       │       │   ├── DistributedFileSystem
│       │       │       │       │   ├── FileHistory
│       │       │       │       │   ├── FileSystem
│       │       │       │       │   ├── Imapi
│       │       │       │       │   ├── IndexServer
│       │       │       │       │   ├── InstallableFileSystems
│       │       │       │       │   ├── IscsiDisc
│       │       │       │       │   ├── Jet
│       │       │       │       │   ├── Nvme
│       │       │       │       │   ├── OfflineFiles
│       │       │       │       │   ├── OperationRecorder
│       │       │       │       │   ├── Packaging
│       │       │       │       │   │   └── Appx
│       │       │       │       │   ├── ProjectedFileSystem
│       │       │       │       │   ├── StructuredStorage
│       │       │       │       │   ├── Vhd
│       │       │       │       │   └── Xps
│       │       │       │       ├── System
│       │       │       │       │   ├── AddressBook
│       │       │       │       │   ├── Antimalware
│       │       │       │       │   ├── ApplicationInstallationAndServicing
│       │       │       │       │   ├── ApplicationVerifier
│       │       │       │       │   ├── ClrHosting
│       │       │       │       │   ├── Com
│       │       │       │       │   │   ├── Marshal
│       │       │       │       │   │   ├── StructuredStorage
│       │       │       │       │   │   └── Urlmon
│       │       │       │       │   ├── ComponentServices
│       │       │       │       │   ├── Console
│       │       │       │       │   ├── CorrelationVector
│       │       │       │       │   ├── DataExchange
│       │       │       │       │   ├── DeploymentServices
│       │       │       │       │   ├── DeveloperLicensing
│       │       │       │       │   ├── Diagnostics
│       │       │       │       │   │   ├── Ceip
│       │       │       │       │   │   ├── Debug
│       │       │       │       │   │   │   └── Extensions
│       │       │       │       │   │   ├── Etw
│       │       │       │       │   │   ├── ProcessSnapshotting
│       │       │       │       │   │   ├── ToolHelp
│       │       │       │       │   │   └── TraceLogging
│       │       │       │       │   ├── DistributedTransactionCoordinator
│       │       │       │       │   ├── Environment
│       │       │       │       │   ├── ErrorReporting
│       │       │       │       │   ├── EventCollector
│       │       │       │       │   ├── EventLog
│       │       │       │       │   ├── EventNotificationService
│       │       │       │       │   ├── GroupPolicy
│       │       │       │       │   ├── HostCompute
│       │       │       │       │   ├── HostComputeNetwork
│       │       │       │       │   ├── HostComputeSystem
│       │       │       │       │   ├── Hypervisor
│       │       │       │       │   ├── IO
│       │       │       │       │   ├── Iis
│       │       │       │       │   ├── Ioctl
│       │       │       │       │   ├── JobObjects
│       │       │       │       │   ├── Js
│       │       │       │       │   ├── Kernel
│       │       │       │       │   ├── LibraryLoader
│       │       │       │       │   ├── Mailslots
│       │       │       │       │   ├── Mapi
│       │       │       │       │   ├── Memory
│       │       │       │       │   │   └── NonVolatile
│       │       │       │       │   ├── MessageQueuing
│       │       │       │       │   ├── MixedReality
│       │       │       │       │   ├── Ole
│       │       │       │       │   ├── PasswordManagement
│       │       │       │       │   ├── Performance
│       │       │       │       │   │   └── HardwareCounterProfiling
│       │       │       │       │   ├── Pipes
│       │       │       │       │   ├── Power
│       │       │       │       │   ├── ProcessStatus
│       │       │       │       │   ├── Recovery
│       │       │       │       │   ├── Registry
│       │       │       │       │   ├── RemoteDesktop
│       │       │       │       │   ├── RemoteManagement
│       │       │       │       │   ├── RestartManager
│       │       │       │       │   ├── Restore
│       │       │       │       │   ├── Rpc
│       │       │       │       │   ├── Search
│       │       │       │       │   │   └── Common
│       │       │       │       │   ├── SecurityCenter
│       │       │       │       │   ├── Services
│       │       │       │       │   ├── SetupAndMigration
│       │       │       │       │   ├── Shutdown
│       │       │       │       │   ├── StationsAndDesktops
│       │       │       │       │   ├── SubsystemForLinux
│       │       │       │       │   ├── SystemInformation
│       │       │       │       │   ├── SystemServices
│       │       │       │       │   ├── Threading
│       │       │       │       │   ├── Time
│       │       │       │       │   ├── TpmBaseServices
│       │       │       │       │   ├── UserAccessLogging
│       │       │       │       │   ├── Variant
│       │       │       │       │   ├── VirtualDosMachines
│       │       │       │       │   ├── WindowsProgramming
│       │       │       │       │   └── Wmi
│       │       │       │       ├── UI
│       │       │       │       │   ├── Accessibility
│       │       │       │       │   ├── ColorSystem
│       │       │       │       │   ├── Controls
│       │       │       │       │   │   └── Dialogs
│       │       │       │       │   ├── HiDpi
│       │       │       │       │   ├── Input
│       │       │       │       │   │   ├── Ime
│       │       │       │       │   │   ├── KeyboardAndMouse
│       │       │       │       │   │   ├── Pointer
│       │       │       │       │   │   ├── Touch
│       │       │       │       │   │   └── XboxController
│       │       │       │       │   ├── InteractionContext
│       │       │       │       │   ├── Magnification
│       │       │       │       │   ├── Shell
│       │       │       │       │   │   ├── Common
│       │       │       │       │   │   └── PropertiesSystem
│       │       │       │       │   ├── TabletPC
│       │       │       │       │   ├── TextServices
│       │       │       │       │   └── WindowsAndMessaging
│       │       │       │       └── Web
│       │       │       │           └── InternetExplorer
│       │       │       └── core
│       │       ├── windows-sys-0.48.0
│       │       │   └── src
│       │       │       ├── Windows
│       │       │       │   ├── Wdk
│       │       │       │   │   └── System
│       │       │       │   │       └── OfflineRegistry
│       │       │       │   └── Win32
│       │       │       │       ├── Data
│       │       │       │       │   ├── HtmlHelp
│       │       │       │       │   ├── RightsManagement
│       │       │       │       │   └── Xml
│       │       │       │       │       ├── MsXml
│       │       │       │       │       └── XmlLite
│       │       │       │       ├── Devices
│       │       │       │       │   ├── AllJoyn
│       │       │       │       │   ├── BiometricFramework
│       │       │       │       │   ├── Bluetooth
│       │       │       │       │   ├── Communication
│       │       │       │       │   ├── DeviceAccess
│       │       │       │       │   ├── DeviceAndDriverInstallation
│       │       │       │       │   ├── DeviceQuery
│       │       │       │       │   ├── Display
│       │       │       │       │   ├── Enumeration
│       │       │       │       │   │   └── Pnp
│       │       │       │       │   ├── Fax
│       │       │       │       │   ├── FunctionDiscovery
│       │       │       │       │   ├── Geolocation
│       │       │       │       │   ├── HumanInterfaceDevice
│       │       │       │       │   ├── ImageAcquisition
│       │       │       │       │   ├── PortableDevices
│       │       │       │       │   ├── Properties
│       │       │       │       │   ├── Pwm
│       │       │       │       │   ├── Sensors
│       │       │       │       │   ├── SerialCommunication
│       │       │       │       │   ├── Tapi
│       │       │       │       │   ├── Usb
│       │       │       │       │   └── WebServicesOnDevices
│       │       │       │       ├── Foundation
│       │       │       │       ├── Gaming
│       │       │       │       ├── Globalization
│       │       │       │       ├── Graphics
│       │       │       │       │   ├── Dwm
│       │       │       │       │   ├── Gdi
│       │       │       │       │   ├── Hlsl
│       │       │       │       │   ├── OpenGL
│       │       │       │       │   └── Printing
│       │       │       │       │       └── PrintTicket
│       │       │       │       ├── Management
│       │       │       │       │   └── MobileDeviceManagementRegistration
│       │       │       │       ├── Media
│       │       │       │       │   ├── Audio
│       │       │       │       │   │   ├── Apo
│       │       │       │       │   │   ├── DirectMusic
│       │       │       │       │   │   ├── Endpoints
│       │       │       │       │   │   └── XAudio2
│       │       │       │       │   ├── DeviceManager
│       │       │       │       │   ├── DxMediaObjects
│       │       │       │       │   ├── KernelStreaming
│       │       │       │       │   ├── LibrarySharingServices
│       │       │       │       │   ├── MediaPlayer
│       │       │       │       │   ├── Multimedia
│       │       │       │       │   ├── Speech
│       │       │       │       │   ├── Streaming
│       │       │       │       │   └── WindowsMediaFormat
│       │       │       │       ├── NetworkManagement
│       │       │       │       │   ├── Dhcp
│       │       │       │       │   ├── Dns
│       │       │       │       │   ├── InternetConnectionWizard
│       │       │       │       │   ├── IpHelper
│       │       │       │       │   ├── MobileBroadband
│       │       │       │       │   ├── Multicast
│       │       │       │       │   ├── Ndis
│       │       │       │       │   ├── NetBios
│       │       │       │       │   ├── NetManagement
│       │       │       │       │   ├── NetShell
│       │       │       │       │   ├── NetworkDiagnosticsFramework
│       │       │       │       │   ├── NetworkPolicyServer
│       │       │       │       │   ├── P2P
│       │       │       │       │   ├── QoS
│       │       │       │       │   ├── Rras
│       │       │       │       │   ├── Snmp
│       │       │       │       │   ├── WNet
│       │       │       │       │   ├── WebDav
│       │       │       │       │   ├── WiFi
│       │       │       │       │   ├── WindowsConnectNow
│       │       │       │       │   ├── WindowsConnectionManager
│       │       │       │       │   ├── WindowsFilteringPlatform
│       │       │       │       │   ├── WindowsFirewall
│       │       │       │       │   └── WindowsNetworkVirtualization
│       │       │       │       ├── Networking
│       │       │       │       │   ├── ActiveDirectory
│       │       │       │       │   ├── BackgroundIntelligentTransferService
│       │       │       │       │   ├── Clustering
│       │       │       │       │   ├── HttpServer
│       │       │       │       │   ├── Ldap
│       │       │       │       │   ├── NetworkListManager
│       │       │       │       │   ├── RemoteDifferentialCompression
│       │       │       │       │   ├── WebSocket
│       │       │       │       │   ├── WinHttp
│       │       │       │       │   ├── WinInet
│       │       │       │       │   ├── WinSock
│       │       │       │       │   └── WindowsWebServices
│       │       │       │       ├── Security
│       │       │       │       │   ├── AppLocker
│       │       │       │       │   ├── Authentication
│       │       │       │       │   │   └── Identity
│       │       │       │       │   │       └── Provider
│       │       │       │       │   ├── Authorization
│       │       │       │       │   │   └── UI
│       │       │       │       │   ├── ConfigurationSnapin
│       │       │       │       │   ├── Credentials
│       │       │       │       │   ├── Cryptography
│       │       │       │       │   │   ├── Catalog
│       │       │       │       │   │   ├── Certificates
│       │       │       │       │   │   ├── Sip
│       │       │       │       │   │   └── UI
│       │       │       │       │   ├── DiagnosticDataQuery
│       │       │       │       │   ├── DirectoryServices
│       │       │       │       │   ├── EnterpriseData
│       │       │       │       │   ├── ExtensibleAuthenticationProtocol
│       │       │       │       │   ├── Isolation
│       │       │       │       │   ├── LicenseProtection
│       │       │       │       │   ├── NetworkAccessProtection
│       │       │       │       │   ├── Tpm
│       │       │       │       │   ├── WinTrust
│       │       │       │       │   └── WinWlx
│       │       │       │       ├── Storage
│       │       │       │       │   ├── Cabinets
│       │       │       │       │   ├── CloudFilters
│       │       │       │       │   ├── Compression
│       │       │       │       │   ├── DataDeduplication
│       │       │       │       │   ├── DistributedFileSystem
│       │       │       │       │   ├── EnhancedStorage
│       │       │       │       │   ├── FileHistory
│       │       │       │       │   ├── FileServerResourceManager
│       │       │       │       │   ├── FileSystem
│       │       │       │       │   ├── Imapi
│       │       │       │       │   ├── IndexServer
│       │       │       │       │   ├── InstallableFileSystems
│       │       │       │       │   ├── IscsiDisc
│       │       │       │       │   ├── Jet
│       │       │       │       │   ├── OfflineFiles
│       │       │       │       │   ├── OperationRecorder
│       │       │       │       │   ├── Packaging
│       │       │       │       │   │   ├── Appx
│       │       │       │       │   │   └── Opc
│       │       │       │       │   ├── ProjectedFileSystem
│       │       │       │       │   ├── StructuredStorage
│       │       │       │       │   ├── Vhd
│       │       │       │       │   ├── VirtualDiskService
│       │       │       │       │   ├── Vss
│       │       │       │       │   └── Xps
│       │       │       │       │       └── Printing
│       │       │       │       ├── System
│       │       │       │       │   ├── AddressBook
│       │       │       │       │   ├── Antimalware
│       │       │       │       │   ├── ApplicationInstallationAndServicing
│       │       │       │       │   ├── ApplicationVerifier
│       │       │       │       │   ├── AssessmentTool
│       │       │       │       │   ├── ClrHosting
│       │       │       │       │   ├── Com
│       │       │       │       │   │   ├── CallObj
│       │       │       │       │   │   ├── ChannelCredentials
│       │       │       │       │   │   ├── Events
│       │       │       │       │   │   ├── Marshal
│       │       │       │       │   │   ├── StructuredStorage
│       │       │       │       │   │   ├── UI
│       │       │       │       │   │   └── Urlmon
│       │       │       │       │   ├── ComponentServices
│       │       │       │       │   ├── Console
│       │       │       │       │   ├── Contacts
│       │       │       │       │   ├── CorrelationVector
│       │       │       │       │   ├── DataExchange
│       │       │       │       │   ├── DeploymentServices
│       │       │       │       │   ├── DesktopSharing
│       │       │       │       │   ├── DeveloperLicensing
│       │       │       │       │   ├── Diagnostics
│       │       │       │       │   │   ├── Ceip
│       │       │       │       │   │   ├── ClrProfiling
│       │       │       │       │   │   ├── Debug
│       │       │       │       │   │   │   ├── ActiveScript
│       │       │       │       │   │   │   └── Extensions
│       │       │       │       │   │   ├── Etw
│       │       │       │       │   │   ├── ProcessSnapshotting
│       │       │       │       │   │   └── ToolHelp
│       │       │       │       │   ├── DistributedTransactionCoordinator
│       │       │       │       │   ├── Environment
│       │       │       │       │   ├── ErrorReporting
│       │       │       │       │   ├── EventCollector
│       │       │       │       │   ├── EventLog
│       │       │       │       │   ├── EventNotificationService
│       │       │       │       │   ├── GroupPolicy
│       │       │       │       │   ├── HostCompute
│       │       │       │       │   ├── HostComputeNetwork
│       │       │       │       │   ├── HostComputeSystem
│       │       │       │       │   ├── Hypervisor
│       │       │       │       │   ├── IO
│       │       │       │       │   ├── Iis
│       │       │       │       │   ├── Ioctl
│       │       │       │       │   ├── JobObjects
│       │       │       │       │   ├── Js
│       │       │       │       │   ├── Kernel
│       │       │       │       │   ├── LibraryLoader
│       │       │       │       │   ├── Mailslots
│       │       │       │       │   ├── Mapi
│       │       │       │       │   ├── Memory
│       │       │       │       │   │   └── NonVolatile
│       │       │       │       │   ├── MessageQueuing
│       │       │       │       │   ├── MixedReality
│       │       │       │       │   ├── Mmc
│       │       │       │       │   ├── Ole
│       │       │       │       │   ├── ParentalControls
│       │       │       │       │   ├── PasswordManagement
│       │       │       │       │   ├── Performance
│       │       │       │       │   │   └── HardwareCounterProfiling
│       │       │       │       │   ├── Pipes
│       │       │       │       │   ├── Power
│       │       │       │       │   ├── ProcessStatus
│       │       │       │       │   ├── RealTimeCommunications
│       │       │       │       │   ├── Recovery
│       │       │       │       │   ├── Registry
│       │       │       │       │   ├── RemoteAssistance
│       │       │       │       │   ├── RemoteDesktop
│       │       │       │       │   ├── RemoteManagement
│       │       │       │       │   ├── RestartManager
│       │       │       │       │   ├── Restore
│       │       │       │       │   ├── Rpc
│       │       │       │       │   ├── Search
│       │       │       │       │   │   └── Common
│       │       │       │       │   ├── SecurityCenter
│       │       │       │       │   ├── ServerBackup
│       │       │       │       │   ├── Services
│       │       │       │       │   ├── SettingsManagementInfrastructure
│       │       │       │       │   ├── SetupAndMigration
│       │       │       │       │   ├── Shutdown
│       │       │       │       │   ├── StationsAndDesktops
│       │       │       │       │   ├── SubsystemForLinux
│       │       │       │       │   ├── SystemInformation
│       │       │       │       │   ├── SystemServices
│       │       │       │       │   ├── TaskScheduler
│       │       │       │       │   ├── Threading
│       │       │       │       │   ├── Time
│       │       │       │       │   ├── TpmBaseServices
│       │       │       │       │   ├── UpdateAgent
│       │       │       │       │   ├── UpdateAssessment
│       │       │       │       │   ├── UserAccessLogging
│       │       │       │       │   ├── VirtualDosMachines
│       │       │       │       │   ├── WindowsProgramming
│       │       │       │       │   ├── WindowsSync
│       │       │       │       │   └── Wmi
│       │       │       │       ├── UI
│       │       │       │       │   ├── Accessibility
│       │       │       │       │   ├── Animation
│       │       │       │       │   ├── ColorSystem
│       │       │       │       │   ├── Controls
│       │       │       │       │   │   ├── Dialogs
│       │       │       │       │   │   └── RichEdit
│       │       │       │       │   ├── HiDpi
│       │       │       │       │   ├── Input
│       │       │       │       │   │   ├── Ime
│       │       │       │       │   │   ├── Ink
│       │       │       │       │   │   ├── KeyboardAndMouse
│       │       │       │       │   │   ├── Pointer
│       │       │       │       │   │   ├── Radial
│       │       │       │       │   │   ├── Touch
│       │       │       │       │   │   └── XboxController
│       │       │       │       │   ├── InteractionContext
│       │       │       │       │   ├── LegacyWindowsEnvironmentFeatures
│       │       │       │       │   ├── Magnification
│       │       │       │       │   ├── Notifications
│       │       │       │       │   ├── Ribbon
│       │       │       │       │   ├── Shell
│       │       │       │       │   │   ├── Common
│       │       │       │       │   │   └── PropertiesSystem
│       │       │       │       │   ├── TabletPC
│       │       │       │       │   ├── TextServices
│       │       │       │       │   ├── WindowsAndMessaging
│       │       │       │       │   └── Wpf
│       │       │       │       └── Web
│       │       │       │           └── InternetExplorer
│       │       │       └── core
│       │       ├── windows-targets
│       │       │   └── src
│       │       ├── windows_aarch64_gnullvm
│       │       │   ├── lib
│       │       │   └── src
│       │       ├── windows_aarch64_msvc
│       │       │   ├── lib
│       │       │   └── src
│       │       ├── windows_i686_gnu
│       │       │   ├── lib
│       │       │   └── src
│       │       ├── windows_i686_msvc
│       │       │   ├── lib
│       │       │   └── src
│       │       ├── windows_x86_64_gnu
│       │       │   ├── lib
│       │       │   └── src
│       │       ├── windows_x86_64_gnullvm
│       │       │   ├── lib
│       │       │   └── src
│       │       ├── windows_x86_64_msvc
│       │       │   ├── lib
│       │       │   └── src
│       │       ├── winnow
│       │       │   ├── examples
│       │       │   │   ├── arithmetic
│       │       │   │   ├── c_expression
│       │       │   │   ├── css
│       │       │   │   ├── http
│       │       │   │   ├── ini
│       │       │   │   ├── json
│       │       │   │   ├── ndjson
│       │       │   │   ├── s_expression
│       │       │   │   └── string
│       │       │   └── src
│       │       │       ├── _topic
│       │       │       ├── _tutorial
│       │       │       ├── ascii
│       │       │       ├── binary
│       │       │       │   └── bits
│       │       │       ├── combinator
│       │       │       │   └── debug
│       │       │       ├── macros
│       │       │       ├── stream
│       │       │       └── token
│       │       ├── wit-bindgen
│       │       │   └── src
│       │       │       ├── examples
│       │       │       └── rt
│       │       │           └── async_support
│       │       ├── zerocopy
│       │       │   ├── agent_docs
│       │       │   ├── benches
│       │       │   │   └── formats
│       │       │   ├── ci
│       │       │   ├── githooks
│       │       │   ├── rustdoc
│       │       │   ├── src
│       │       │   │   ├── pointer
│       │       │   │   └── util
│       │       │   ├── testdata
│       │       │   │   └── include_value
│       │       │   └── tests
│       │       │       └── ui
│       │       ├── zerocopy-derive
│       │       │   ├── src
│       │       │   │   ├── derive
│       │       │   │   └── output_tests
│       │       │   │       └── expected
│       │       │   └── tests
│       │       │       └── ui
│       │       │           └── cfgs
│       │       ├── zeroize
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── zip
│       │       │   ├── benches
│       │       │   ├── examples
│       │       │   ├── src
│       │       │   │   └── read
│       │       │   └── tests
│       │       │       └── data
│       │       ├── zmij
│       │       │   ├── benches
│       │       │   ├── src
│       │       │   └── tests
│       │       ├── zstd
│       │       │   ├── assets
│       │       │   ├── examples
│       │       │   └── src
│       │       │       ├── bulk
│       │       │       └── stream
│       │       │           ├── read
│       │       │           ├── write
│       │       │           └── zio
│       │       ├── zstd-safe
│       │       │   └── src
│       │       └── zstd-sys
│       │           ├── src
│       │           ├── wasm-shim
│       │           └── zstd
│       │               ├── contrib
│       │               │   └── seekable_format
│       │               └── lib
│       │                   ├── common
│       │                   ├── compress
│       │                   ├── decompress
│       │                   ├── deprecated
│       │                   ├── dictBuilder
│       │                   └── legacy
│       ├── out
│       └── regex
├── internal
│   └── source
│       └── modules
│           └── auxiliary
│               ├── bruteforce
│               │   └── telnet
│               ├── dos
│               │   ├── ftp
│               │   └── smtp
│               ├── fuzzers
│               │   ├── dns
│               │   └── http
│               ├── proxy
│               │   ├── http
│               │   └── https
│               └── voip
│                   ├── dos
│                   └── scan
├── lib
│   ├── core
│   │   ├── commands
│   │   └── database
│   ├── roar
│   │   ├── callbin
│   │   ├── logging
│   │   │   └── src
│   │   └── plugin
│   ├── smf
│   │   ├── core
│   │   │   ├── booting
│   │   │   ├── console
│   │   │   ├── sf
│   │   │   │   └── cache
│   │   │   └── verify
│   │   │       └── src
│   │   └── ssl
│   ├── smfdb_helpers
│   ├── sqlite
│   │   ├── cached
│   │   ├── logging
│   │   └── storage
│   └── ui
│       └── console
├── modules
│   ├── auxiliary
│   │   ├── brute
│   │   │   ├── ftp
│   │   │   ├── hash
│   │   │   ├── ssh
│   │   │   ├── telnet
│   │   │   └── web
│   │   │       └── grafana
│   │   ├── dos
│   │   │   ├── ftp
│   │   │   ├── http
│   │   │   └── smtp
│   │   ├── fuzzers
│   │   │   ├── dns
│   │   │   └── http
│   │   ├── proxy
│   │   │   └── https
│   │   ├── scanner
│   │   │   ├── fortinet
│   │   │   └── net
│   │   ├── splunk
│   │   │   └── PostgreSQL
│   │   └── voip
│   └── exploit
│       ├── android
│       │   └── adb
│       ├── bac
│       └── http
│           └── Splunk
├── plugin
├── script
├── scripts
│   ├── cpl
│   └── security
│       └── src
└── tests

1755 directories
```
