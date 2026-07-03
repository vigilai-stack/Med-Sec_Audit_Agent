"""
Orchestrator Supervisor
Coordinates all agents and manages the audit pipeline
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from src.mcp_server import MCPSandboxServer
from src.agents import RedTeamAgent, BlueTeamAgent, GreenTeamAgent, ComplianceAgent
from src.config import config


class OrchestratorSupervisor:
    """
    Orchestrator that coordinates the multi-agent audit pipeline
    
    Audit Phases:
    1. Baseline Establishment (Blue Team)
    2. Adversarial Testing (Red Team)
    3. Threat Detection (Blue Team)
    4. Auto-Remediation (Green Team)
    5. Compliance Verification (Compliance Agent)
    """
    
    def __init__(self, attack_templates: Optional[Dict[str, list]] = None):
        self.sandbox = MCPSandboxServer()
        self.red_team = RedTeamAgent(self.sandbox, attack_templates=attack_templates)
        self.blue_team = BlueTeamAgent(self.sandbox)
        self.green_team = GreenTeamAgent(self.sandbox)
        self.compliance_agent = ComplianceAgent(self.sandbox)
        
        self.audit_results = {}
        self.start_time = None
        self.end_time = None
        self.state = "IDLE"
        
        print("\n🏥 [Orchestrator] Initializing Med-Sec Audit Agent")
        print("   ✅ Red Team: Ready (Adversarial Testing)")
        print("   ✅ Blue Team: Ready (Threat Monitoring)")
        print("   ✅ Green Team: Ready (Auto-Remediation)")
        print("   ✅ Compliance: Ready (HIPAA/HITECH)")
        print(f"   ✅ Sandbox: {config.workspace_dir}")
    
    def run_full_audit(self, target_system: str, patient_record: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run the complete audit pipeline
        
        Args:
            target_system: Name of the system being audited
            patient_record: Optional patient record for compliance testing
        
        Returns:
            Complete audit results
        """
        self.start_time = datetime.now()
        self.state = "RUNNING"
        
        print("\n" + "=" * 70)
        print(f"🏥 MED-SEC AUDIT AGENT - Full Security Audit")
        print(f"   Target: {target_system}")
        print(f"   Started: {self.start_time.isoformat()}")
        print("=" * 70 + "\n")
        
        # Phase 1: Baseline Establishment
        print("\n📊 Phase 1: Baseline Establishment...")
        baseline_log = "User: admin access patient_record\nUser: doctor_smith access patient_record"
        self.audit_results["baseline"] = self.blue_team.establish_baseline(baseline_log)
        
        # Phase 2: Red Team Security Audit
        print("\n🔴 Phase 2: Red Team Security Audit...")
        self.audit_results["red_team"] = self.red_team.run_full_audit(target_system)
        
        # Phase 3: Blue Team Threat Detection
        print("\n🔵 Phase 3: Blue Team Threat Detection...")
        activity_log = "User: unknown_user access patient_record\nUser: attacker ' OR '1'='1'"
        self.audit_results["blue_team"] = self.blue_team.monitor_activity(activity_log)
        
        # Phase 4: Green Team Auto-Remediation
        print("\n🟢 Phase 4: Green Team Auto-Remediation...")
        vulns = [
            {"type": "PHI_EXFILTRATION", "severity": "HIGH"},
            {"type": "PROMPT_INJECTION", "severity": "CRITICAL"}
        ]
        self.audit_results["green_team"] = [
            self.green_team.remediate_vulnerability(v) for v in vulns
        ]
        
        # Phase 5: Compliance Verification
        print("\n📋 Phase 5: Compliance Verification...")
        if patient_record is None:
            patient_record = {
                "patient_id": "MRN-123456",
                "name": "John Smith",
                "dob": "01/15/1980",
                "ssn": "123-45-6789",
                "phone": "555-123-4567",
                "email": "john.smith@email.com"
            }
        anonymized = self.sandbox.tool_anonymize_patient_record(patient_record)
        self.audit_results["phi_anonymization"] = anonymized
        compliance_record = anonymized.get("anonymized_record", patient_record)
        self.audit_results["compliance"] = self.compliance_agent.validate_compliance(
            compliance_record, "HIPAA"
        )
        
        self.end_time = datetime.now()
        self.state = "COMPLETED"
        
        print("\n" + "=" * 70)
        print("✅ AUDIT COMPLETED!")
        print(f"   Duration: {(self.end_time - self.start_time).total_seconds():.1f} seconds")
        print("=" * 70)
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate a comprehensive audit summary"""
        risk_level = self.audit_results.get("red_team", {}).get("overall_risk", {}).get("level", "UNKNOWN")
        threat_count = self.audit_results.get("blue_team", {}).get("threat_count", 0)
        fixes_applied = len(self.audit_results.get("green_team", []))
        compliance_score = self.audit_results.get("compliance", {}).get("compliance_score", 0)
        
        # Calculate remediation success rate
        green_successes = sum(1 for f in self.audit_results.get("green_team", []) if f.get("fix_applied", False))
        green_total = max(len(self.audit_results.get("green_team", [])), 1)
        
        summary = {
            "audit_id": f"MEDSEC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            "risk_assessment": {
                "overall_risk": risk_level,
                "threats_detected": threat_count
            },
            "remediation": {
                "fixes_applied": fixes_applied,
                "success_rate": green_successes / green_total
            },
            "compliance": {
                "score": compliance_score * 100,
                "compliant": compliance_score >= 0.8
            },
            "recommendations": [
                "Implement stricter input validation",
                "Enforce least privilege access",
                "Enable MFA for all admin users",
                "Regular security awareness training",
                "Conduct quarterly penetration tests"
            ],
            "raw_results": self.audit_results
        }
        
        # Save report
        report_path = os.path.join(config.workspace_dir, "reports", f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n📄 Report saved: {report_path}")
        
        log_path = os.path.join(config.workspace_dir, "logs", "audit_log.json")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "w") as f:
            json.dump(self.sandbox.audit_log, f, indent=2, default=str)
        print(f"Audit log saved: {log_path}")

        return summary
    
    def get_agent_metrics(self) -> Dict:
        """Get metrics from all agents"""
        return {
            "red_team": self.red_team.metrics,
            "blue_team": self.blue_team.metrics,
            "green_team": self.green_team.metrics,
            "compliance": self.compliance_agent.metrics
        }
