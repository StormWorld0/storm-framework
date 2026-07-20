# --- Configuration ---
OUT := $(OUT_DIR)/core/CRS

# --- Source Discovery ---
ALL_SRCS   := $(shell find . -type f -name '*.go')
MAIN_SRCS := $(shell grep -l "func main()" $(ALL_SRCS) 2>/dev/null)

MAIN_COUNT := $(words $(MAIN_SRCS))
MAIN_FILE  := $(firstword $(MAIN_SRCS))
MAIN_DIR   := $(dir $(MAIN_FILE))
TARGET     := $(OUT)/$(basename $(notdir $(MAIN_FILE)))

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(ALL_SRCS)
	@mkdir -p "$(OUT)"
	@go build -o "$(TARGET)" "$(MAIN_DIR)"

clean:
	rm -rf "$(OUT)"
