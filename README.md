# Cylc-8_SPEAR_Basic_QC_Workflow_Example

# SPEAR 6-Hour Precipitation Basic QC Demo/Example

A Cylc 8 workflow demonstrating automated quality control (QC) on
GFDL-SPEAR-MED 6-hour precipitation output.

## Overview

This workflow performs:

1. Metadata validation
2. Rogue pixel threshold detection
3. Optional alert plot generation
4. Automated reporting and packaging

Just a ightweight reproducible example of model output QC!

---

## Workflow Structure

setup → metadata_qc → scan_rogue_pixels → summarize → gate → package

---

## Example Dataset

This demo expects a NetCDF file such as:

pr_6hr_GFDL-SPEAR-MED_historical_*.nc

(Example files not included in repo...)

---

## Installation

```bash
conda env create -f environment.yml
conda activate spear-qc
