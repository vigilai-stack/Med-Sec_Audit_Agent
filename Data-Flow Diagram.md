                        User Request
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 1. CONFIGURATION & SETUP                                            │
│    ├── Mount Google Drive                                           │
│    ├── Load configuration (config.yaml)                             │
│    ├── Load environment variables (.env)                            │
│    └── Initialize RAG Knowledge Base                                │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. DATA LOADING                                                     │
│    ├── Load patient records (CSV)                                   │
│    ├── Load attack payloads (CSV)                                   │
│    └── Validate PHI detection patterns                              │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. BLUE TEAM: BASELINE ESTABLISHMENT                                │
│    ├── Analyze EHR access logs                                      │
│    ├── Identify normal user behavior                                │
│    └── Store baseline profile                                       │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. RED TEAM: ADVERSARIAL TESTING                                    │
│    ├── PHI Exfiltration attacks                                     │
│    ├── Prompt Injection attacks                                     │
│    ├── Privilege Escalation attempts                                │
│    ├── SQL Injection attempts                                       │
│    └── Path Traversal attempts                                      │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. BLUE TEAM: THREAT DETECTION                                      │
│    ├── Monitor EHR access logs                                      │
│    ├── Compare against baseline                                     │
│    ├── Detect anomalies                                             │
│    ├── Identify threats                                             │
│    └── Assign risk scores                                           │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. GREEN TEAM: AUTO-REMEDIATION                                     │
│    ├── Identify vulnerability type                                  │
│    ├── Apply security patch                                         │
│    ├── Validate fix                                                 │
│    └── Log remediation                                              │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. COMPLIANCE AGENT: HIPAA VALIDATION                               │
│    ├── Validate Privacy Rule                                        │
│    ├── Validate Security Rule                                       │
│    ├── Check breach notification                                    │
│    ├── Verify encryption                                            │
│    ├── Check audit logging                                          │
│    └── Generate compliance score                                    │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 8. REPORT GENERATION                                                │
│    ├── Generate executive summary                                   │
│    ├── Create visualizations                                        │
│    ├── Export to JSON, CSV, HTML, DOCX, PDF                         │
│    └── Save reports to Google Drive                                 │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                ✅ RETURN TO USER (Audit Complete)