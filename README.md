# Cylc-8_SPEAR_Basic_QC_Workflow_Example

# SPEAR 6-Hour Precipitation Basic QC Demo/Example

A Cylc 8 workflow demonstrating automated quality control (QC) on
GFDL-SPEAR-MED 6-hour precipitation output.

### Overview

This workflow performs:

1. Metadata validation
2. Rogue pixel threshold detection
3. Optional alert plot generation
4. Automated reporting and output file creation

Just a ightweight reproducible example of model output QC!

---

### Workflow Structure

setup → metadata_qc → scan_rogue_pixels → summarize → create output files

---

### Example Dataset

This demo expects a NetCDF file such as:

pr_6hr_GFDL-SPEAR-MED_historical_*.nc

(Example files not included in repo...)

---

# Installation and Setup (On Workstation)
### 1. On your workstation, clone the repo:
```bash
git clone <repo_link>
```
### 2. Load Conda:
```bash
module load conda
```

### 3. Create and activate the cylc env:
```bash
conda create -n spear-qc-demo -y -c conda-forge python=3.11 
conda activate spear-qc-demo 
```
### 4. Install Packages:
```bash
conda install -y -c conda-forge mamba
mamba install -y -c conda-forge cylc-flow netcdf4 numpy pyyaml matplotlib cartopy 
```

### 5. Edit the workflow config (flow.cylc) as needed (input file name/location, QC thresold value, etc.)
```bash
vi Cylc-8_SPEAR_Basic_QC_Workflow_Example/cylc-src/spear-qc-demo/flow.cylc
```

### 6. Create cylc-run directory in /work
```bash
mkdir -p /work/FIRST.LAST/cylc-run
```

### 7. Create cylc config directory
```bash
mkdir -p ~/.cylc/flow
```

### 8. Copy example cylc config file to the cylc config directory, modify as needed:
```bash
cp Cylc-8_SPEAR_Basic_QC_Workflow_Example/cylc-src/spear-qc-demo/global.cylc ~/.cylc/flow
```

### 9. Run it:
```bash
cylc validate .
cylc install --workflow-name=spear-qc-demo .
cylc play spear-qc-demo
```

### 10. Check live progress of tasks with: 
```bash
cylc tui spear-qc-demo/run1
```

### 11. Output (like report.txt) written to:
```bash
~/cylc-run/spear-qc/runN/work/
```
### 12. To stop a run:
```bash
cylc stop --now spear-qc-demo/runN
```

### 13. To clean (needed before restarting, removes previous run output and logs)
```bash
cylc clean spear-qc-demo/runN
```

### 14. Output PNGs are located here:
```bash
/work/FIRST.LAST/cylc-run/cylc-run/spear-qc-demo/run1/outputs
```
### 15. Output report.txt file is located here:
```bash
/work/FIRST.LAST/cylc-run/cylc-run/spear-qc-demo/run1/work
```
