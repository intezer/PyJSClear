#!/bin/bash -eu
# OSS-Fuzz build script for pyjsclear
# See https://google.github.io/oss-fuzz/getting-started/new-project-guide/python-lang/

# Install project and dependencies
pip3 install .
pip3 install atheris

# Copy fuzz targets and helpers to $OUT
cp tests/fuzz/fuzz_*.py "$OUT/"
cp tests/fuzz/conftest_fuzz.py "$OUT/"

# Build seed corpus zips
TARGETS=(deobfuscate parser generator transforms expression_simplifier string_decoders scope traverser)

for target in "${TARGETS[@]}"; do
    corpus_dir="tests/fuzz/seed_corpus"

    # Map target to its corpus directory
    case "$target" in
        deobfuscate|expression_simplifier|transforms)
            src_dir="$corpus_dir/deobfuscate"
            ;;
        parser|generator|scope|traverser)
            src_dir="$corpus_dir/parser"
            ;;
        string_decoders)
            src_dir="$corpus_dir/string_decoders"
            ;;
        *)
            src_dir="$corpus_dir/deobfuscate"
            ;;
    esac

    if [ -d "$src_dir" ] && [ "$(ls -A "$src_dir")" ]; then
        zip -j "$OUT/fuzz_${target}_seed_corpus.zip" "$src_dir"/*
    fi
done
