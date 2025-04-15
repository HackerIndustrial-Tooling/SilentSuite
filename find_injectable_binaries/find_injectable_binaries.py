#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def is_executable(path):
    return os.access(path, os.X_OK) and os.path.isfile(path)

def is_dyld_injectable(path):
    try:
        output = subprocess.check_output(
            ["codesign", "-dvv", path],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        hardened = "Runtime hardened: yes" in output #Need to go off the codes instead 
        libval = "Library Validation: Yes" in output
        return not (hardened or libval)
    except subprocess.CalledProcessError:
        return False  # Not signed? Possibly injectable.

def scan_paths(paths):
    injectable = []
    for base_path in paths:
        for root, _, files in os.walk(base_path):
            for f in files:
                full_path = os.path.join(root, f)
                if is_executable(full_path) and is_dyld_injectable(full_path):
                    injectable.append(full_path)
    return injectable

if __name__ == "__main__":
    print("[*] Scanning for DYLD-injectable binaries...")
    scan_targets = [
        "/Applications",
        "/usr/local/bin",
        "/opt/homebrew/bin",
        "/usr/bin",  # carefully — might find Apple tools (mostly not injectable)
        str(Path.home()),
    ]
    found = scan_paths(scan_targets)

    if not found:
        print("[-] No injectable binaries found.")
    else:
        print(f"[+] Found {len(found)} injectable binaries:\n")
        for path in found:
            print(f"    {path}")
