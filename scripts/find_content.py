"""
find_content.py — reproduce the negative result in docs/import/content-inventory.md §5.

Searches for the PABC consolidated encounter-builder export: any file carrying
the marker strings that identify the engine's table-grouped JSON.

Usage:  python scripts/find_content.py [root ...]
Default roots: the current user's home directory, and the E: drive

Prints every hit plus a scan count, so a zero-hit result is falsifiable rather
than merely asserted.
"""
import os, sys, json

MARKERS = ("world_encounters", "quest_beat_prereqs", "SET_PLAYER_FLAG")
EXTS = (".json", ".jsonl", ".txt", ".md", ".js", ".jsx", ".html", ".csv", ".sql")
SKIP_DIRS = {
    "$RECYCLE.BIN", "System Volume Information", "node_modules", ".git",
    "__pycache__", "SteamLibrary", "Windows", "Program Files",
    "Program Files (x86)", "AppData", "VortexMods", "Movies", "Shows",
    "Raw video", "LUTs", "ComfyUI",
}
MIN_BYTES, MAX_BYTES, READ_BYTES = 3_000, 80_000_000, 400_000


def scan(root):
    hits, scanned = [], 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.lower().endswith(EXTS):
                continue
            full = os.path.join(dirpath, name)
            try:
                size = os.path.getsize(full)
                if not (MIN_BYTES <= size <= MAX_BYTES):
                    continue
                scanned += 1
                with open(full, encoding="utf-8", errors="replace") as fh:
                    head = fh.read(READ_BYTES)
            except OSError:
                continue
            found = [m for m in MARKERS if m in head]
            if found:
                hits.append({"path": full, "bytes": size, "markers": found})
    return hits, scanned


def main():
    roots = sys.argv[1:] or [os.path.expanduser("~"), "E:\\"]
    all_hits, total = [], 0
    for root in roots:
        if not os.path.isdir(root):
            print(f"  (skipped, not a directory: {root})")
            continue
        hits, scanned = scan(root)
        total += scanned
        all_hits.extend(hits)
        print(f"  {root}: {scanned} files read, {len(hits)} hits")

    print(f"\n{total} files scanned, {len(all_hits)} hits total")
    for h in all_hits:
        print(json.dumps(h, indent=2))
    if not all_hits:
        print("\nNo consolidated encounter-builder export found on this machine.")


if __name__ == "__main__":
    main()
