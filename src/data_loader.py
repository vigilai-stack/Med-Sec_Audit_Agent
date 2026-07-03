"""
Data Loader
Loads patient data, payload data, configuration, and environment variables
"""

import os
import ast
import yaml
import pandas as pd
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def load_env(env_path: str) -> None:
    """Load environment variables from .env file"""
    if os.path.exists(env_path):
        load_dotenv(env_path)


def load_patient_data(data_path: str) -> List[Dict]:
    """Load patient data from CSV file"""
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        # Convert string representations of lists back to actual lists
        for col in ['conditions', 'medications']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
        return df.to_dict('records')
    return []


def load_payload_data(data_path: str) -> pd.DataFrame:
    """Load attack payloads from CSV file"""
    if os.path.exists(data_path):
        return pd.read_csv(data_path)
    return pd.DataFrame()


def save_output(data: Any, output_path: str, filename: str) -> str:
    """Save output data to file"""
    os.makedirs(output_path, exist_ok=True)
    filepath = os.path.join(output_path, filename)
    if isinstance(data, (dict, list)):
        import json
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    elif isinstance(data, pd.DataFrame):
        data.to_csv(filepath, index=False)
    else:
        with open(filepath, 'w') as f:
            f.write(str(data))
    return filepath
