"""
Configuration Loader
Loads settings from config.yaml and environment variables
"""

import os
import yaml
from dotenv import load_dotenv
from pathlib import Path


class Config:
    """Central configuration manager for the Med-Sec Audit Agent"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Load configuration from yaml and environment"""
        # Load environment variables
        load_dotenv()

        # Get base path. If .env points to a Colab/Drive path that is not
        # available locally, fall back to the project root/current directory.
        env_base = os.getenv("BASE_PATH", os.getcwd())
        if not os.path.exists(os.path.join(env_base, "config.yaml")):
            env_base = os.getcwd()
        self.base_path = env_base

        # Load YAML config
        config_path = os.path.join(self.base_path, "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            self._config = self._get_default_config()

        # Input data stays in Data/. All generated artifacts stay in medsec_sandbox/.
        self.data_path = os.path.join(self.base_path, "Data")
        self.patient_data_path = os.path.join(self.data_path, "patient_records.csv")
        self.payload_data_path = os.path.join(self.data_path, "payloads.csv")
        self.sandbox_path = os.path.join(self.base_path, "medsec_sandbox")
        self.output_path = os.path.join(self.sandbox_path, "output")
        self.logs_path = os.path.join(self.sandbox_path, "logs")
        self.reports_path = os.path.join(self.sandbox_path, "reports")
        self.test_data_path = os.path.join(self.sandbox_path, "test_data")

        # Create generated-artifact directories
        for path in [self.sandbox_path, self.output_path, self.logs_path, self.reports_path, self.test_data_path]:
            os.makedirs(path, exist_ok=True)

    def _get_default_config(self):
        """Return default configuration if config.yaml not found"""
        return {
            "project": {"name": "Med-Sec Audit Agent", "version": "1.0.0"},
            "orchestrator": {
                "audit_phases": [
                    "baseline_establishment",
                    "adversarial_testing",
                    "threat_detection",
                    "auto_remediation",
                    "compliance_verification"
                ],
                "parallel_execution": False,
                "log_level": "INFO"
            },
            "blue_team": {
                "metrics": ["data_quality", "completeness", "consistency", "accuracy"],
                "threshold": 0.95
            },
            "red_team": {
                "payload_types": ["sql_injection", "xss", "command_injection", "path_traversal"],
                "severity_levels": ["low", "medium", "high", "critical"]
            },
            "green_team": {
                "auto_fix": True,
                "backup_before_fix": True,
                "max_attempts": 3
            },
            "compliance": {
                "regulations": ["HIPAA", "GDPR", "FDA_21_CFR_Part_11"],
                "strict_mode": True
            },
            "mcp_server": {
                "host": "localhost",
                "port": 8000,
                "timeout": 30,
                "max_connections": 10
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "medsec_sandbox/logs/audit.log"
            }
        }

    def get(self, key, default=None):
        """Get a configuration value by dot-notation key"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @property
    def workspace_dir(self):
        return self.sandbox_path

    @property
    def encryption_enabled(self):
        return self.get('security.encryption_enabled', True)

    @property
    def phi_masking_enabled(self):
        return self.get('security.phi_masking_enabled', True)

    @property
    def audit_log_enabled(self):
        return self.get('security.audit_log_enabled', True)


# Singleton instance
config = Config()

