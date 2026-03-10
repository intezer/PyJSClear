#!/bin/bash
# Local fuzzing runner for pyjsclear
#
# Usage:
#   ./tests/fuzz/run_local.sh fuzz_deobfuscate 60    # run for 60 seconds
#   ./tests/fuzz/run_local.sh fuzz_parser 30          # run for 30 seconds
#   ./tests/fuzz/run_local.sh all 10                  # run all targets for 10 seconds each

set -e

FUZZ_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$FUZZ_DIR")")"

# Use python3 explicitly (python may not exist on some systems)
PYTHON="${PYTHON:-python3}"

TARGET="${1:-fuzz_deobfuscate}"
DURATION="${2:-10}"

# Map targets to seed corpus directories
get_corpus_dir() {
    local target="$1"
    case "$target" in
        fuzz_deobfuscate|fuzz_expression_simplifier|fuzz_transforms)
            echo "$FUZZ_DIR/seed_corpus/deobfuscate"
            ;;
        fuzz_parser|fuzz_generator|fuzz_scope|fuzz_traverser)
            echo "$FUZZ_DIR/seed_corpus/parser"
            ;;
        fuzz_string_decoders)
            echo "$FUZZ_DIR/seed_corpus/string_decoders"
            ;;
        *)
            echo "$FUZZ_DIR/seed_corpus/deobfuscate"
            ;;
    esac
}

run_target() {
    local target="$1"
    local duration="$2"
    local corpus_dir
    corpus_dir="$(get_corpus_dir "$target")"
    local work_corpus="$FUZZ_DIR/corpus/$target"

    mkdir -p "$work_corpus"

    echo "========================================="
    echo "Running $target for ${duration}s"
    echo "Seed corpus: $corpus_dir"
    echo "Work corpus: $work_corpus"
    echo "========================================="

    cd "$PROJECT_DIR"

    # Check if atheris is available
    if "$PYTHON" -c "import atheris" 2>/dev/null; then
        # Run with atheris/libFuzzer
        "$PYTHON" "$FUZZ_DIR/${target}.py" \
            "$work_corpus" "$corpus_dir" \
            -max_total_time="$duration" \
            -timeout=30 \
            -rss_limit_mb=2048 \
            -max_len=102400
    else
        # Run with standalone fuzzer
        "$PYTHON" "$FUZZ_DIR/${target}.py" \
            "$corpus_dir" \
            -max_total_time="$duration" \
            -max_len=102400 \
            -timeout=30 \
            -rss_limit_mb=2048
    fi

    echo ""
}

if [ "$TARGET" = "all" ]; then
    TARGETS=(fuzz_deobfuscate fuzz_parser fuzz_generator fuzz_transforms fuzz_expression_simplifier fuzz_string_decoders fuzz_scope fuzz_traverser)
    for t in "${TARGETS[@]}"; do
        run_target "$t" "$DURATION"
    done
else
    run_target "$TARGET" "$DURATION"
fi
