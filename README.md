### Double Decompress DICOM Files (MRI → NIfTI Ready)

This repository provides a robust batch-processing pipeline for preparing MRI DICOM files reliable for conversion to NIfTI (`.nii.gz`) format.

Many standard DICOM → NIfTI tools fail when encountering compressed, encapsulated, or vendor-specific DICOM files. This project solves that problem by **decompressing the DICOMs twice using GDCM** before conversion.

### Pipeline Overview

#### Step 1: Python GDCM Decompression
- Reads DICOM files using Python GDCM bindings
- Preserves metadata
- Writes partially decompressed DICOM files

#### Step 2: Raw Decompression (`gdcmconv --raw`)
- Forces raw pixel storage
- Removes encapsulation
- Produces fully uncompressed DICOMs
  
The output files are now safe for NIfTI conversion.

#### Folder Structure
```text
Input DICOM Folders
└── Scan Name - 1/
    ├── image001.dcm
└── Scan Name - 2/
    ├── image002.dcm
```

### How to Run
1. Navigate to the directory containing all DICOM folders.
   ``` bash
   cd /path/to/folder
   ```
3. Run the pipeline:
   ```bash
   python3 double_decompress.py
   ```
4. This will generate two folders:
   a. PY-DECOMP
   b. DICOM_READY_FOR_NIFTI
5. Convert the second folder to NIfTI using dcm2niix:
   ```bash
   mkdir Nifti
   dcm2niix -o Nifti -z y -f <subjectID>_%d_%s_raw DICOM_READY_FOR_NIFTI
   ```
   

