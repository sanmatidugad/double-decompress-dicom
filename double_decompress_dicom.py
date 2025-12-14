#!/usr/bin/env python3
"""
DICOM Double Decompression Pipeline

This script prepares MRI DICOM files for reliable conversion to NIfTI format
by performing a two-stage decompression using GDCM:

1. Python GDCM ImageReader/ImageWriter decompression
2. GDCM CLI raw decompression (gdcmconv --raw)

Output DICOMs are fully uncompressed, explicit VR, and compatible with
standard DICOM-to-NIfTI converters (e.g., dcm2niix).
"""

import os    # files system operations
import re    # regular expressions for extracting series number
import subprocess    # run command-line
import gdcm    # Python bindings for the Grassroots DICOM library (used to read/write DICOM images)
from pathlib import Path    # Get File Paths

# ==============================
# Configuration
# ==============================

PY_DECOMP_DIR = Path("PY-DECOMP")
DICOM_READY_DIR = Path("DICOM_READY_FOR_NIFTI")    # Final Folder Name

SERIES_PATTERN = re.compile(r" - (\d+)")
DICOM_EXTENSION = ".dcm"


# ==============================
# Utility Functions
# ==============================

def find_first_dicom(directory: Path) -> Path | None:
    """Return the first .dcm file found in a directory."""
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() == DICOM_EXTENSION:
            return file
    return None


def python_decompress_dicom(input_dicom: Path, output_dicom: Path) -> bool:
    """
    Decompress a DICOM file using Python GDCM while preserving metadata.
    """
    reader = gdcm.ImageReader()
    reader.SetFileName(str(input_dicom))

    if not reader.Read():
        print(f"[ERROR] Failed to read DICOM: {input_dicom}")
        return False

    writer = gdcm.ImageWriter()
    writer.SetFileName(str(output_dicom))
    writer.SetFile(reader.GetFile())   # Preserve original tags
    writer.SetImage(reader.GetImage()) # Uncompressed image data

    if not writer.Write():
        print(f"[ERROR] Failed to write DICOM: {output_dicom}")
        return False

    return True


def raw_decompress_dicom(input_dicom: Path, output_dicom: Path) -> bool:
    """
    Fully decompress a DICOM file using gdcmconv --raw.
    """
    command = ["gdcmconv", "--raw", str(input_dicom), str(output_dicom)]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as error:
        print(f"[ERROR] gdcmconv failed for {input_dicom}")
        print(error.stderr.decode())
        return False


# ==============================
# Main Pipeline
# ==============================

def main() -> None:
    """
    Execute the double decompression pipeline.
    """
    PY_DECOMP_DIR.mkdir(exist_ok=True)
    DICOM_READY_DIR.mkdir(exist_ok=True)

    print("\n=== Stage 1: Python GDCM Decompression ===\n")

    for item in Path.cwd().iterdir():
        if not item.is_dir():
            continue

        match = SERIES_PATTERN.search(item.name)
        if not match:
            print(f"[SKIP] {item.name} — no series number found.")
            continue

        series_number = match.group(1)
        dicom_file = find_first_dicom(item)

        if dicom_file is None:
            print(f"[SKIP] {item.name} — no DICOM files found.")
            continue

        output_dicom = PY_DECOMP_DIR / f"pydecompressed_{series_number}.dcm"

        print(f"[INFO] Processing series {series_number}")
        if python_decompress_dicom(dicom_file, output_dicom):
            print(f"[OK] Wrote {output_dicom}")
        else:
            print(f"[FAIL] Python decompression failed for series {series_number}")

    print("\n=== Stage 2: Raw GDCM Decompression ===\n")

    for dicom_file in PY_DECOMP_DIR.glob("*.dcm"):
        output_dicom = DICOM_READY_DIR / dicom_file.name.replace( "pydecompressed", "raw")

        if raw_decompress_dicom(dicom_file, output_dicom):
            print(f"[OK] Raw decompressed: {output_dicom}")
        else:
            print(f"[FAIL] Raw decompression failed: {dicom_file}")

    print("\n=== Pipeline Complete ===")
    print(f"Final output directory: {DICOM_READY_DIR.resolve()}\n")


# ==============================
# Entry Point
# ==============================

if __name__ == "__main__":
    main()

