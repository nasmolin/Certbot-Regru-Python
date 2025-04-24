#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
from datetime import datetime
from log_utils import log

def copy_artifacts(paths, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    missing = False

    for path in paths:
        name = os.path.basename(path.rstrip("/"))
        target_path = os.path.join(output_dir, name)

        if os.path.isdir(path):
            try:
                shutil.copytree(path, target_path, dirs_exist_ok=True)
                log("success", f"Copied directory {path} → {target_path}")
            except Exception as e:
                log("error", f"Failed to copy directory {path}: {e}")
                missing = True
        elif os.path.isfile(path):
            try:
                shutil.copy2(path, target_path)
                log("success", f"Copied file {path} → {target_path}")
            except Exception as e:
                log("error", f"Failed to copy file {path}: {e}")
                missing = True
        else:
            log("error", f"Path not found: {path}")
            missing = True

    if missing:
        log("error", "One or more paths failed to copy. Failing job.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy files/directories to artifacts directory.")
    parser.add_argument("--output", required=True, help="Output directory for artifacts")
    parser.add_argument("--paths", nargs="+", required=True, help="List of paths to include in artifacts")
    args = parser.parse_args()

    copy_artifacts(args.paths, args.output)