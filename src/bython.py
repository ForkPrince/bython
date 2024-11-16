import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path
import parser

VERSION_NUMBER = "1.0"

"""
Bython is Python with braces.

This is a command-line utility to translate and run Bython files.

Flags and arguments:
    -V, --version:      Print version number
    -v, --verbose:      Print progress
    -c, --compile:      Translate to Python file and store; do not run
    -k, --keep:         Keep generated Python files
    -t, --lower_true:   Adds support for lowercase true/false
    -2, --python2:      Use python2 instead of python3
    -o, --output:       Specify name of output directory
    input:              File or directory to process
"""

def main():
    arg_parser = argparse.ArgumentParser(
        prog="bython",
        description="Bython is a Python preprocessor that translates braces into indentation",
        formatter_class=argparse.RawTextHelpFormatter
    )

    arg_parser.add_argument("-V", "--version", action="version", version=f"Bython v{VERSION_NUMBER}\nOriginally by Mathias Lohne and Tristan Pepin 2018\nForked by prushton2")
    arg_parser.add_argument("-v", "--verbose", help="Print progress", action="store_true")
    arg_parser.add_argument("-c", "--compile", help="Translate to Python only (don't run files)", action="store_true")
    arg_parser.add_argument("-k", "--keep", help="Keep generated Python files after running", action="store_true")
    arg_parser.add_argument("-t", "--truefalse", help="Add support for lowercase true/false and null for None", action="store_true")
    arg_parser.add_argument("-2", "--python2", help="Use python2 instead of python3 (default)", action="store_true")
    arg_parser.add_argument("-e", "--entry-point", type=str, help="Specify entry point. Default is ./main.py")
    arg_parser.add_argument("-o", "--output", type=str, help="Specify name of output directory", default=".bython")
    arg_parser.add_argument("input", type=str, help="File or directory to process")

    args = arg_parser.parse_args()

    python_cmd = "python2" if args.python2 else "python3"
    output_dir = Path(args.output)

    if output_dir.exists():
        if args.verbose:
            print(f"Removing existing directory: {output_dir}")
        shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    entry_point = args.entry_point or "main.py"
    entry_executed = False

    def log(message):
        if args.verbose:
            print(message)

    def parse_and_run(source, dest):
        """Parse a Bython file and optionally run it."""
        parser.parse_file(source, dest, args.truefalse)
        log(f"Parsed: {source} -> {dest}")
        if not args.compile:
            subprocess.run([python_cmd, dest])
            return True
        return False

    input_path = Path(args.input)

    if input_path.is_file() and input_path.suffix == ".by":
        output_file = output_dir / "main.py"
        entry_executed = parse_and_run(input_path, output_file)
    elif input_path.is_dir():
        files = list(input_path.glob("**/*"))
        for file in files:
            relative_path = file.relative_to(input_path)
            dest_path = output_dir / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if file.is_file():
                if file.suffix == ".by":
                    dest_path = dest_path.with_suffix(".py")
                    parse_and_run(file, dest_path)
                else:
                    shutil.copy(file, dest_path)
                    log(f"Copied: {file} -> {dest_path}")
    else:
        print(f"Error: Input path '{input_path}' is not a valid file or directory.")
        sys.exit(1)

    if not entry_executed and not args.compile:
        entry_file = output_dir / entry_point
        if entry_file.exists():
            log(f"Running entry point: {entry_file}")
            subprocess.run([python_cmd, str(entry_file)])
        else:
            print(f"Error: Entry point '{entry_file}' not found.")
            sys.exit(1)

    if not args.keep and not args.compile:
        log(f"Cleaning up: Removing {output_dir}")
        shutil.rmtree(output_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
