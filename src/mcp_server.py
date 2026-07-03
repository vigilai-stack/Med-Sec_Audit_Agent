"""
MCP Server Implementation
Secure, sandboxed tools for healthcare security auditing
"""

import os
import re
import json
import uuid
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict


class PHIPatterns:
    """PHI detection patterns for healthcare data"""
    
    PATTERNS = {
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "dob": r'\b\d{2}/\d{2}/\d{4}\b',
        "phone": r'\b\d{3}-\d{3}-\d{4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "mrn": r'\bMRN-\d{6,}\b',
        "address": r'\b\d{1,5}\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct)\b',
        "medicare_id": r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',
        # 'name' is LAST to avoid matching "Oak Street" as a name before address can match
        "name": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
    }


class SecurityUtils:
    """Security utilities for PHI masking and audit logging"""
    
    @staticmethod
    def mask_phi(text: str) -> Tuple[str, Dict]:
        """Mask PHI in text and return masked text with found PHI"""
        masked_text = text
        phi_found = {}
        
        for phi_type, pattern in PHIPatterns.PATTERNS.items():
            matches = re.findall(pattern, masked_text)
            if matches:
                phi_found[phi_type] = matches
                for match in matches:
                    placeholder = f"[[{phi_type.upper()}_{hashlib.md5(match.encode()).hexdigest()[:8]}]]"
                    masked_text = masked_text.replace(match, placeholder)
        
        return masked_text, phi_found
    
    @staticmethod
    def generate_audit_trail(action: str, agent: str, status: str, details: Dict) -> Dict:
        """Generate an immutable audit trail entry"""
        return {
            "timestamp": datetime.now().isoformat(),
            "audit_id": str(uuid.uuid4()),
            "agent": agent,
            "action": action,
            "status": status,
            "details": details,
            "hash": hashlib.sha256(json.dumps(details).encode()).hexdigest()
        }
    
    @staticmethod
    def validate_input_safety(text: str) -> bool:
        """Check if input contains dangerous patterns"""
        dangerous_patterns = [
            r'<script', r'javascript:', r'DROP TABLE', r';--', 
            r'--', r'/\*', r'\*/', r'UNION SELECT'
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True


class MCPSandboxServer:
    """
    MCP Server providing secure, sandboxed tools for healthcare auditing
    
    Tools:
    - anonymize_patient_record: Mask PHI in patient records
    - detect_threat: Scan logs for security threats
    - compliance_check: Validate HIPAA compliance
    """
    
    def __init__(self, workspace: str = None):
        from src.config import config
        self.workspace = workspace or config.workspace_dir
        self.audit_log = []
        self.tool_usage_stats = defaultdict(int)
        
        # Create workspace directories
        os.makedirs(os.path.join(self.workspace, "crypto"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace, "quarantine"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace, "logs"), exist_ok=True)
    
    def tool_anonymize_patient_record(self, record: Dict) -> Dict[str, Any]:
        """Anonymize PHI in a patient record"""
        start_time = time.perf_counter()
        self.tool_usage_stats["anonymize"] += 1
        
        try:
            result = {
                "status": "success",
                "anonymized_record": {},
                "phi_found": {},
                "original_phi_count": 0
            }
            
            for key, value in record.items():
                if isinstance(value, str):
                    masked_value, phi_found = SecurityUtils.mask_phi(value)
                    result["anonymized_record"][key] = masked_value
                    if phi_found:
                        result["phi_found"].update(phi_found)
                        result["original_phi_count"] += len(phi_found)
                else:
                    result["anonymized_record"][key] = value
            
            result["runtime_ms"] = (time.perf_counter() - start_time) * 1000
            self.audit_log.append(SecurityUtils.generate_audit_trail(
                "anonymize", "mcp_server", "success", {"phi_count": result["original_phi_count"]}
            ))
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "runtime_ms": (time.perf_counter() - start_time) * 1000
            }
    
    def tool_detect_threat(self, log_data: str) -> Dict[str, Any]:
        """Detect security threats in log data"""
        start_time = time.perf_counter()
        self.tool_usage_stats["detect_threat"] += 1
        
        try:
            threats = []
            risk_score = 0.0
            
            # Check for unusual PHI access
            phi_accesses = re.findall(r'access.*PHI|view.*patient|read.*record', log_data, re.IGNORECASE)
            if len(phi_accesses) > 10:
                threats.append(f"Unusual PHI access pattern: {len(phi_accesses)} accesses")
                risk_score += 0.3
            
            # Check for injection attempts
            injection_patterns = ["' OR '1'='1", "; DROP TABLE", "UNION SELECT", "'; --"]
            for pattern in injection_patterns:
                if pattern in log_data:
                    threats.append(f"Potential SQL injection attempt: {pattern}")
                    risk_score += 0.5
                    break
            
            # Check for suspicious users
            suspicious_users = re.findall(r'user:\s*(unknown|attacker|guest|hacker)', log_data, re.IGNORECASE)
            if suspicious_users:
                threats.append(f"Suspicious user detected: {suspicious_users[0]}")
                risk_score += 0.2
            
            result = {
                "status": "success",
                "threats_found": threats,
                "risk_score": min(1.0, risk_score),
                "threat_count": len(threats),
                "severity": "HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.3 else "LOW",
                "runtime_ms": (time.perf_counter() - start_time) * 1000
            }
            
            self.audit_log.append(SecurityUtils.generate_audit_trail(
                "detect_threat", "mcp_server", "success", {"threat_count": len(threats)}
            ))
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def tool_compliance_check(self, record: Dict, standard: str = "HIPAA") -> Dict[str, Any]:
        """Check compliance with healthcare regulations"""
        start_time = time.perf_counter()
        self.tool_usage_stats["compliance_check"] += 1
        
        try:
            compliance_issues = []
            passed_checks = 0
            total_checks = 0
            
            # Check 1: PHI detection
            record_str = json.dumps(record)
            masked, phi_found = SecurityUtils.mask_phi(record_str)
            if phi_found:
                compliance_issues.append(f"PHI detected in record: {list(phi_found.keys())}")
            else:
                passed_checks += 1
            total_checks += 1
            
            # Check 2: Encryption
            from src.config import config
            if config.encryption_enabled:
                passed_checks += 1
            else:
                compliance_issues.append("Encryption disabled")
            total_checks += 1
            
            # Check 3: Audit logging
            if config.audit_log_enabled:
                passed_checks += 1
            else:
                compliance_issues.append("Audit logging disabled")
            total_checks += 1
            
            # Check 4: Access controls (basic check)
            if "access" in record or "permission" in record:
                passed_checks += 1
            total_checks += 1
            
            compliance_score = passed_checks / max(total_checks, 1)
            
            result = {
                "status": "success",
                "standard": standard,
                "compliance_score": compliance_score,
                "passed_checks": passed_checks,
                "total_checks": total_checks,
                "issues_found": compliance_issues,
                "compliant": compliance_score >= 0.8,
                "runtime_ms": (time.perf_counter() - start_time) * 1000
            }
            
            self.audit_log.append(SecurityUtils.generate_audit_trail(
                "compliance_check", "mcp_server", "pass" if result["compliant"] else "fail",
                {"score": compliance_score}
            ))
            return result
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_tool_stats(self) -> Dict:
        """Get statistics on tool usage"""
        return {
            "total_audit_entries": len(self.audit_log),
            "tool_usage": dict(self.tool_usage_stats),
            "last_audit": self.audit_log[-1] if self.audit_log else None
        }