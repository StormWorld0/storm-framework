# --- Configuration ---
OUT := $(OUT_DIR)/core/CRS

# --- Source Discovery ---
ALL_SRCS   := $(shell find . -type f -name '*.go')
MAIN_SRCS  := $(shell grep -lE '^[[:space:]]*func[[:space:]]+main[[:space:]]*\(' $(ALL_SRCS) 2>/dev/null)

MAIN_COUNT := $(words $(MAIN_SRCS))
MAIN_FILE  := $(firstword $(MAIN_SRCS))
MAIN_DIR   := $(dir $(MAIN_FILE))
TARGET     := $(OUT)/$(basename $(notdir $(MAIN_FILE)))

.PHONY: all clean

all:
	@mkdir -p "$(OUT)"
	@go build -o "$(TARGET)" "$(MAIN_DIR)"

clean:
	rm -rf "$(OUT)"
