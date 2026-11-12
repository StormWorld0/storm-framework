.SILENT:

NAME     := verified
OUT_DIR  ?= build
OUT      := $(OUT_DIR)/core/integrity
TARGET   := $(OUT)/$(NAME)

# Cargo target cache resolution
CACHE    := $(CARGO_TARGET_DIR)
ifeq ($(CACHE),)
    CACHE := target
endif

# --- HARDWARE OPTIMIZATION LAYER ---
# Compile-on-Device Paradigm: 
# Forces the LLVM backend of rustc to evaluate the local instruction set 
# (CPUID for x86_64, or MIDR_EL1 for ARM64) and inject 
# absolute microarchitectural optimization without Makefile intervention.
export RUSTFLAGS := -C target-cpu=native

SRC      := $(shell find src -name "*.rs" 2>/dev/null) Cargo.toml

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	mkdir -p $(OUT)
	cargo build --release --offline --quiet
	cp $(CACHE)/release/$(NAME) $(TARGET)
	strip $(TARGET)

clean:
	cargo clean --quiet
	rm -f $(TARGET)
