# Kaggle Capstone Project - June 2026

## Orchestrator Supervisor for Healthcare Data Security & Compliance Audit Pipeline

### Project Overview
This project implements an automated audit pipeline with five phases:
1. **Baseline Establishment (Blue Team)** - Data quality assessment
2. **Adversarial Testing (Red Team)** - Security vulnerability testing
3. **Threat Detection (Blue Team)** - Anomaly detection
4. **Auto-Remediation (Green Team)** - Automated fixes
5. **Compliance Verification (Compliance Agent)** - Regulatory compliance check

---

## Prerequisites

- Google account with Google Drive access
- Google Colab (free tier is sufficient)
- Internet connection

---

## Setup Instructions

## Step 1: Access the Project Files

1. Accept the Google Drive folder sharing invitation
2. Navigate to `Kaggle_Capstone_Project_June_2026/`
3. Verify the following structure exists:
Kaggle_Capstone_Project_June_2026/
├── Capstone_Notebook.ipynb
├── requirements.txt
├── config.yaml
├── .env.template
├── README.md
└── Data/
├── patient_records.csv
└── payloads.csv


## Step 2: Open the Notebook in Colab

1. Right-click on `Capstone_Notebook.ipynb`
2. Select **Open with** → **Google Colaboratory**
3. If Colab is not available, go to **More apps** and install it


## Step 3: Mount Google Drive

In the first cell of the notebook, run:
```python
from google.colab import drive
drive.mount('/content/drive')


## Step 4: Set Up Environment Variables

 1. Copy .env.template to .env:
!cp /content/drive/MyDrive/Kaggle_Capstone_Project_June_2026/.env.template /content/drive/MyDrive/Kaggle_Capstone_Project_June_2026/.env

 2. Edit .env to add your API keys (if needed)


## Step 5: Install Dependencies

Run the installation cell in the notebook:
!pip install -r /content/drive/MyDrive/Kaggle_Capstone_Project_June_2026/requirements.txt


## Step 6: Verify Data Files

Check that the data files exist:
python
import os
BASE = "/content/drive/MyDrive/Kaggle_Capstone_Project_June_2026/"
print(os.listdir(BASE + "Data/"))


## Step 7: Run the Complete Pipeline

Execute all cells in sequence from top to bottom.


Project Structure

Kaggle_Capstone_Project_June_2026/
│
├── Capstone_Notebook.ipynb          # Main orchestrator notebook
├── requirements.txt                  # Python dependencies
├── config.yaml                       # Central configuration
├── .env.template                     # Environment variables template
├── README.md                         # This file
│
└── Data/
    ├── patient_records.csv           # Patient records (required)
    └── payloads.csv                  # Attack payloads (required)


Troubleshooting
Issue: ModuleNotFoundError

Solution: Re-run the installation cell or install specific packages manually:

!pip install package_name


Issue: FileNotFoundError

Solution: Check that your Google Drive is mounted and paths are correct:

!ls /content/drive/MyDrive/Kaggle_Capstone_Project_June_2026/Data/

Issue: Memory/Resource Errors in Colab

Solution: Restart the runtime and run cells in order. Consider using Colab Pro for larger datasets.


Issue: Different Paths on Teammate's Machine

Solution: The BASE_PATH variable should be updated in the notebook's first cell. Each user should verify their drive path.

# Getting Help
1. Check the inline comments in the notebook
2. Review the config.yaml for adjustable parameters
3. Contact the Team Mate to discuss issues and figure out solution(s).


# Version History
Version 1.0 - June 2026 - Initial release








