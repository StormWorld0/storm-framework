.SILENT:

RAW_NAME := smf
NAME     := smf.$(EXT)
OUT_DIR  ?= build
OUT      := $(OUT_ROOT)
TARGET   := $(OUT)/$(NAME)

# Cargo cache path resolution
CACHE    := $(CARGO_TARGET_DIR)
ifeq ($(CACHE),)
    CACHE := target
endif

# Source code resolution for re-compile trigger
SRC      := $(shell find src -name "*.rs" 2>/dev/null) Cargo.toml

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	mkdir -p $(OUT)
	cargo build --release --offline --quiet
	cp $(CACHE)/release/lib$(RAW_NAME).$(EXT) $(TARGET)
	strip --strip-unneeded $(TARGET)

clean:
	cargo clean --quiet
	rm -f $(TARGET)
