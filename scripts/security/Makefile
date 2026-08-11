.SILENT:

RAW_NAME := signed
NAME     := libsigned.$(EXT)
OUT_DIR  ?= build
OUT      := $(OUT_DIR)/core/integrity
TARGET   := $(OUT)/$(NAME)

# Cargo cache path resolution
CACHE    := $(CARGO_TARGET_DIR)
ifeq ($(CACHE),)
    CACHE := target
endif

# --- HARDWARE OPTIMIZATION LAYER ---
# Using the Compile-on-Device paradigm. 
# Delegates 100% of microarchitectural resolution to the host LLVM backend.
# rustc will evaluate CPUID (x86_64) or MIDR_EL1 (ARM64) dynamically 
# to inject the most advanced vector instruction sets (AVX, SVE, NEON) 
# supported by the user's local silicon.
export RUSTFLAGS := -C target-cpu=native

# Source code resolution for re-compile trigger
SRC      := $(shell find src -name "*.rs" 2>/dev/null) Cargo.toml

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	mkdir -p $(OUT)
	cargo build --release --offline --quiet
	cp $(CACHE)/release/lib$(RAW_NAME).so $(TARGET)
	strip --strip-unneeded $(TARGET)

clean:
	cargo clean --quiet
	rm -f $(TARGET)
