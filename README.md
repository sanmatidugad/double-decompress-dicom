### Double Decompress DICOM Files (MRI → NIfTI Ready)

This repository provides a robust pipeline for preparing MRI DICOM files for reliable conversion to NIfTI (`.nii.gz`) format.

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
└── Scan Name - 12/
    ├── image001.dcm
    ├── image002.dcm
```
#### Step 3 – Use the following `dcm2niix` command
``` text
mkdir Nifti
dcm2niix -o Nifti -z y -f <subjectID>_%d_%s_raw DICOM_READY_FOR_NIFTI
```
