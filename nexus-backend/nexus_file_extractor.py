"""
nexus_file_extractor.py — Splits NEXUS_BACKEND_ALL_FILES.txt into individual files.
Usage: python nexus_file_extractor.py NEXUS_BACKEND_ALL_FILES.txt [--output-dir .]
"""
import argparse, os, re, sys

START_PATTERN = re.compile(r"^###\s+FILE:\s+(.+?)\s+###\s*$")
END_PATTERN   = re.compile(r"^###\s+END FILE:\s+(.+?)\s+###\s*$")

def extract(bundle_path, output_dir):
    if not os.path.isfile(bundle_path):
        print(f"[ERROR] Bundle file not found: {bundle_path}", file=sys.stderr); sys.exit(1)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    files_written, current_file, current_lines = [], None, []
    with open(bundle_path, encoding="utf-8", errors="replace") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line        = raw_line.rstrip("\n")
            start_match = START_PATTERN.match(line)
            end_match   = END_PATTERN.match(line)
            if start_match:
                if current_file:
                    _write(output_dir, current_file, current_lines, files_written)
                current_file, current_lines = start_match.group(1).strip(), []
            elif end_match:
                if current_file:
                    _write(output_dir, current_file, current_lines, files_written)
                current_file, current_lines = None, []
            else:
                if current_file is not None:
                    current_lines.append(raw_line)
    if current_file:
        _write(output_dir, current_file, current_lines, files_written)
    print(f"\nExtracted {len(files_written)} file(s) to: {output_dir}")
    for p in files_written: print(f"  -> {p}")

def _write(output_dir, rel_path, lines, registry):
    clean     = os.path.normpath(rel_path).lstrip("/").lstrip("\\")
    full_path = os.path.join(output_dir, clean)
    os.makedirs(os.path.dirname(full_path) or output_dir, exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as fh:
        fh.write("".join(lines))
    registry.append(clean)
    print(f"  -> {clean}")

def main():
    parser = argparse.ArgumentParser(description="Extract NEXUS bundle into source files.")
    parser.add_argument("bundle", nargs="?", default="NEXUS_BACKEND_ALL_FILES.txt")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    extract(args.bundle, args.output_dir)

if __name__ == "__main__":
    main()