"""
Med-Sec Audit Agent Streamlit GUI.

Run from the project root:
    streamlit run app.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
os.environ.setdefault("BASE_PATH", str(PROJECT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import config  # noqa: E402
from src.data_loader import load_patient_data, load_payload_data  # noqa: E402
from src.orchestrator import OrchestratorSupervisor  # noqa: E402

try:
    from src.report_agent import ReportGenerationAgent  # noqa: E402
except Exception:  # pragma: no cover - optional report extras may be missing locally
    ReportGenerationAgent = None

st.set_page_config(
    page_title="Med-Sec Audit Agent",
    page_icon="+",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #172033;
        --muted: #667085;
        --line: #D8DEE9;
        --panel: #FFFFFF;
        --soft: #F5F7FA;
        --navy: #1C2B3A;
        --teal: #0B7A75;
        --red: #C93636;
        --gold: #B7791F;
        --green: #13795B;
    }
    .main .block-container {
        padding-top: 1.1rem;
        padding-bottom: 2.2rem;
        max-width: 1240px;
    }
    section[data-testid="stSidebar"] {
        background: #EEF2F6;
        border-right: 1px solid #D8DEE9;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] label {
        color: #253244;
    }
    .hero {
        border: 1px solid #D7DEE8;
        border-radius: 10px;
        padding: 26px 28px;
        background: linear-gradient(135deg, #FFFFFF 0%, #F7FAFC 52%, #EDF7F6 100%);
        box-shadow: 0 10px 30px rgba(23, 32, 51, 0.06);
        margin-bottom: 18px;
    }
    .eyebrow {
        color: var(--teal);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .hero-title {
        color: var(--ink);
        font-size: 2.25rem;
        line-height: 1.12;
        font-weight: 850;
        margin: 0 0 8px 0;
    }
    .hero-copy {
        color: #526071;
        font-size: 1.02rem;
        max-width: 780px;
        margin-bottom: 12px;
    }
    .tagline {
        display: inline-block;
        border-left: 5px solid #C93636;
        background: #F8FAFC;
        color: #172033;
        padding: 12px 16px 13px 16px;
        margin: 2px 0 18px 0;
        max-width: 800px;
        box-shadow: inset 0 -1px 0 #D8DEE9;
    }
    .tagline-label {
        color: #C93636;
        font-size: 0.72rem;
        line-height: 1.1;
        font-weight: 850;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .tagline-main {
        color: #172033;
        font-size: 1.08rem;
        line-height: 1.28;
        font-weight: 900;
        text-transform: uppercase;
    }
    .tagline-main span {
        color: #0B7A75;
    }
    .chip-row { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: 1px solid #D8DEE9;
        border-radius: 999px;
        padding: 6px 11px;
        background: #FFFFFF;
        color: #344054;
        font-size: 0.83rem;
        font-weight: 650;
    }
    .chip-dot {
        width: 7px;
        height: 7px;
        border-radius: 99px;
        background: var(--teal);
    }
    .metric-card {
        position: relative;
        border: 1px solid #D9E1EA;
        border-radius: 10px;
        padding: 16px 17px 15px 17px;
        background: #FFFFFF;
        min-height: 126px;
        box-shadow: 0 8px 22px rgba(23, 32, 51, 0.045);
        overflow: hidden;
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--accent, var(--teal));
    }
    .metric-label {
        color: #5D6B7B;
        font-size: 0.78rem;
        font-weight: 760;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin: 4px 0 9px 0;
    }
    .metric-value {
        color: var(--ink);
        font-size: 1.7rem;
        line-height: 1.1;
        font-weight: 850;
    }
    .metric-note {
        color: #6B7788;
        font-size: 0.84rem;
        margin-top: 9px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .section-title {
        color: var(--ink);
        font-size: 1.08rem;
        font-weight: 820;
        margin: 22px 0 8px 0;
    }
    .callout {
        border: 1px solid #CFE1EF;
        border-left: 5px solid #2E86AB;
        border-radius: 8px;
        padding: 14px 16px;
        background: #F2F8FC;
        color: #263B4A;
        margin: 14px 0 14px 0;
    }
    .empty-panel {
        border: 1px dashed #BEC8D5;
        border-radius: 10px;
        padding: 24px;
        background: #FFFFFF;
        color: #526071;
        margin-top: 14px;
    }
    .empty-panel strong { color: var(--ink); }
    .sidebar-brand {
        border: 1px solid #D2DAE5;
        border-radius: 10px;
        padding: 14px 14px 13px 14px;
        background: #FFFFFF;
        margin: 4px 0 16px 0;
    }
    .sidebar-brand-title {
        color: var(--ink);
        font-size: 1.02rem;
        font-weight: 850;
        margin-bottom: 4px;
    }
    .sidebar-brand-copy {
        color: #667085;
        font-size: 0.82rem;
        line-height: 1.35;
    }
    .path-pill {
        border-radius: 7px;
        border: 1px solid #D8DEE9;
        background: #F8FAFC;
        padding: 8px 10px;
        color: #526071;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 0.73rem;
        word-break: break-all;
        margin-bottom: 12px;
    }
    div.stButton > button {
        border-radius: 8px;
        min-height: 42px;
        font-weight: 750;
    }
    div.stButton > button[kind="primary"] {
        background: #C93636;
        border: 1px solid #C93636;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #D8DEE9;
        border-radius: 8px;
        overflow: hidden;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #D8DEE9;
        border-radius: 10px;
        padding: 14px 16px;
        background: #FFFFFF;
        box-shadow: 0 8px 22px rgba(23, 32, 51, 0.04);
    }
    div[data-testid="stMetricLabel"] { color: #667085; font-weight: 700; }
    div[data-testid="stMetricValue"] { color: var(--ink); font-size: 1.55rem; }
    .risk-card {
        border-radius: 10px;
        padding: 16px 17px;
        color: #FFFFFF;
        text-align: center;
        box-shadow: 0 8px 22px rgba(23, 32, 51, 0.08);
    }
    .risk-card .risk-label { font-size: 0.78rem; font-weight: 760; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.92; }
    .risk-card .risk-value { font-size: 1.7rem; font-weight: 850; line-height: 1.1; margin-top: 6px; }
    .risk-card .risk-note { font-size: 0.82rem; margin-top: 8px; opacity: 0.88; }
    .risk-LOW { background: #13795B; }
    .risk-MEDIUM { background: #B7791F; }
    .risk-HIGH { background: #E65100; }
    .risk-CRITICAL { background: #C93636; }
    .status-badge {
        display: inline-block;
        border-radius: 999px;
        padding: 4px 11px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #FFFFFF;
    }
    .status-fixed { background: #13795B; }
    .status-pending { background: #B7791F; }
    .status-failed { background: #C93636; }
    .footer-band {
        border-top: 1px solid #D8DEE9;
        margin-top: 28px;
        padding-top: 14px;
        text-align: center;
        color: #667085;
        font-size: 0.82rem;
    }
    .footer-band strong { color: var(--teal); }
    </style>
    """,
    unsafe_allow_html=True,
)


def ensure_workspace() -> None:
    for folder in ["output", "logs", "reports", "test_data", "tmp", "crypto", "quarantine", "kaggle_submission"]:
        (Path(config.workspace_dir) / folder).mkdir(parents=True, exist_ok=True)


def load_data() -> tuple[List[Dict[str, Any]], pd.DataFrame]:
    patients = load_patient_data(config.patient_data_path)
    payloads = load_payload_data(config.payload_data_path)
    return patients, payloads


def payload_templates(payloads: pd.DataFrame) -> Dict[str, List[str]] | None:
    if payloads.empty or not {"category", "payload"}.issubset(payloads.columns):
        return None
    templates = {
        str(category).upper(): group["payload"].dropna().astype(str).head(25).tolist()
        for category, group in payloads.groupby("category")
    }
    return {key: value for key, value in templates.items() if value}


def run_audit(target_system: str, patient_record: Dict[str, Any] | None, payloads: pd.DataFrame) -> Dict[str, Any]:
    templates = payload_templates(payloads)
    orchestrator = OrchestratorSupervisor(attack_templates=templates)
    return orchestrator.run_full_audit(target_system, patient_record=patient_record)


def attach_report_context(results: Dict[str, Any], institution_name: str, report_date, target_system: str) -> Dict[str, Any]:
    results["report_context"] = {
        "institution_name": institution_name.strip() or "Demo Healthcare Institution",
        "report_generated_date": str(report_date),
        "target_system": target_system.strip() or "Healthcare Clinical Documentation System",
        "prepared_by": "Med-Sec Audit Agent (PHI Guardians)",
    }
    return results


def report_dir() -> Path:
    path = Path(config.workspace_dir) / "reports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_reports(results: Dict[str, Any]) -> Dict[str, str]:
    if ReportGenerationAgent is None:
        return {}
    skills_path = PROJECT_ROOT / ".agent" / "skills"
    if not skills_path.exists():
        skills_path = PROJECT_ROOT / ".agents" / "skills"
    agent = ReportGenerationAgent(workspace_dir=config.workspace_dir, skills_path=str(skills_path))
    return agent.generate_report(results, report_format="all") or {}


def create_submission_package(results: Dict[str, Any]) -> Path:
    submission_dir = Path(config.workspace_dir) / "kaggle_submission"
    submission_dir.mkdir(parents=True, exist_ok=True)
    (submission_dir / "audit_results.json").write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    for name in ["reports", "test_data", "logs", "output"]:
        src = Path(config.workspace_dir) / name
        dst = submission_dir / name
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    return submission_dir


def list_artifacts() -> pd.DataFrame:
    rows = []
    for folder in ["reports", "logs", "output", "test_data", "kaggle_submission"]:
        base = Path(config.workspace_dir) / folder
        if not base.exists():
            continue
        for file_path in base.rglob("*"):
            if file_path.is_file():
                rows.append(
                    {
                        "folder": folder,
                        "file": file_path.name,
                        "size_kb": round(file_path.stat().st_size / 1024, 1),
                        "path": str(file_path),
                    }
                )
    return pd.DataFrame(rows)


def file_mime(path: Path) -> str:
    return {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pdf": "application/pdf",
        ".html": "text/html",
        ".json": "application/json",
        ".csv": "text/csv",
        ".png": "image/png",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }.get(path.suffix.lower(), "application/octet-stream")


def download_button(file_path: str, label: str | None = None) -> None:
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return
    st.download_button(
        label=label or f"Download {path.name}",
        data=path.read_bytes(),
        file_name=path.name,
        mime=file_mime(path),
        use_container_width=True,
    )


def report_download_panel(outputs: Dict[str, str]) -> None:
    if not outputs:
        return
    labels = {
        "docx": "Download Word (.docx)",
        "pdf": "Download PDF (.pdf)",
        "xlsx": "Download Excel (.xlsx)",
        "pptx": "Download PowerPoint (.pptx)",
        "html": "Download HTML (.html)",
        "json": "Download JSON (.json)",
    }
    st.subheader("Report Downloads")
    cols = st.columns(3)
    for idx, fmt in enumerate(["docx", "pdf", "xlsx", "pptx", "html", "json"]):
        file_path = outputs.get(fmt)
        if file_path and Path(file_path).exists():
            with cols[idx % 3]:
                download_button(file_path, labels.get(fmt))


def metric_card(label: str, value: str, note: str = "", accent: str = "#0B7A75") -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{accent};">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


ensure_workspace()
patients, payloads = load_data()

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Healthcare AI Security Console</div>
      <div class="hero-title">Med-Sec Audit Agent</div>
      <div class="tagline">
        <div class="tagline-label">Core Promise</div>
        <div class="tagline-main">Data security is not a feature - it's a necessity.<br><span>And now, it's automated.</span></div>
      </div>
      <div class="hero-copy">
        Run a repeatable multi-agent audit across adversarial testing, threat monitoring,
        remediation, PHI masking, and compliance reporting.
      </div>
      <div class="chip-row">
        <span class="chip"><span class="chip-dot"></span>Red Team</span>
        <span class="chip"><span class="chip-dot"></span>Blue Team</span>
        <span class="chip"><span class="chip-dot"></span>Green Team</span>
        <span class="chip"><span class="chip-dot"></span>Compliance</span>
        <span class="chip"><span class="chip-dot"></span>Report Export</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
          <div class="sidebar-brand-title">Audit Setup</div>
          <div class="sidebar-brand-copy">Select a target, choose a patient record, then run the full security audit.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("Project root")
    st.markdown(f'<div class="path-pill">{PROJECT_ROOT}</div>', unsafe_allow_html=True)
    institution_name = st.text_input("Institution name", value="Demo Healthcare Institution")
    report_date = st.date_input("Report date", value=datetime.now().date())
    target_system = st.text_input("Target system", value="Healthcare Clinical Documentation System")
    patient_options = [f"{p.get('mrn', 'N/A')} - {p.get('first_name', '')} {p.get('last_name', '')}" for p in patients]
    selected_idx = st.selectbox(
        "Patient record for compliance test",
        options=list(range(len(patient_options))) if patient_options else [],
        format_func=lambda idx: patient_options[idx],
        disabled=not patient_options,
    )
    st.markdown("---")
    run_clicked = st.button("Run Full Audit", type="primary", use_container_width=True)
    report_clicked = st.button("Generate Reports", use_container_width=True)
    package_clicked = st.button("Build Kaggle Package", use_container_width=True)

patient_record = patients[selected_idx] if patient_options else None

status_cols = st.columns(4)
with status_cols[0]:
    metric_card("Patient records", f"{len(patients):,}", Path(config.patient_data_path).name, "#0B7A75")
with status_cols[1]:
    metric_card("Payloads", f"{len(payloads):,}", Path(config.payload_data_path).name, "#C93636")
with status_cols[2]:
    kb_docs = list((PROJECT_ROOT / "knowledge_base" / "documents").rglob("*")) if (PROJECT_ROOT / "knowledge_base" / "documents").exists() else []
    metric_card("Knowledge files", f"{sum(1 for p in kb_docs if p.is_file()):,}", "RAG source documents", "#2E86AB")
with status_cols[3]:
    metric_card("Workspace", "Ready", "medsec_sandbox", "#13795B")

if "audit_results" not in st.session_state:
    st.session_state.audit_results = None
if "report_outputs" not in st.session_state:
    st.session_state.report_outputs = {}

if run_clicked:
    if not patients:
        st.error("No patient records found. Check Data/patient_records.csv.")
    else:
        with st.spinner("Phase 1/3 — Running multi-agent audit (Red, Blue, Green teams)..."):
            st.session_state.audit_results = attach_report_context(
                run_audit(target_system, patient_record, payloads), institution_name, report_date, target_system
            )
        st.success("Audit completed.")

if report_clicked:
    if not st.session_state.audit_results:
        st.warning("Run an audit before generating reports.")
    else:
        with st.spinner("Phase 2/3 — Generating multi-format reports (PDF, DOCX, XLSX, PPTX, HTML, JSON)..."):
            attach_report_context(st.session_state.audit_results, institution_name, report_date, target_system)
            st.session_state.report_outputs = generate_reports(st.session_state.audit_results)
        if st.session_state.report_outputs:
            st.success("Reports generated.")
        else:
            st.warning("Report agent is unavailable or optional report dependencies are missing.")

if package_clicked:
    if not st.session_state.audit_results:
        st.warning("Run an audit before building the Kaggle package.")
    else:
        with st.spinner("Phase 3/3 — Building Kaggle submission package..."):
            package_dir = create_submission_package(st.session_state.audit_results)
        st.success(f"Kaggle package created: {package_dir}")

results = st.session_state.audit_results

if results:
    risk = results.get("risk_assessment", {})
    remediation = results.get("remediation", {})
    compliance = results.get("compliance", {})
    raw = results.get("raw_results", {})

    section_title("Audit Summary")
    overall_risk = str(risk.get("overall_risk", "UNKNOWN")).upper()
    risk_colors = {"LOW": "#13795B", "MEDIUM": "#B7791F", "HIGH": "#E65100", "CRITICAL": "#C93636"}
    risk_color = risk_colors.get(overall_risk, "#0B7A75")
    threats = risk.get("threats_detected", 0)
    fixes = remediation.get("fixes_applied", 0)
    comp_score = compliance.get("score", 0)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="risk-card risk-{overall_risk}">
              <div class="risk-label">Overall Risk</div>
              <div class="risk-value">{overall_risk}</div>
              <div class="risk-note">Threats: {threats}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        metric_card("Threats Detected", str(threats), "Blue team findings", risk_color)
    with c3:
        metric_card("Fixes Applied", str(fixes), "Green team remediations", "#13795B")
    with c4:
        metric_card("Compliance", f"{comp_score:.1f}%", "HIPAA score", "#2E86AB")

    tab_overview, tab_red, tab_blue, tab_green, tab_compliance, tab_visual, tab_artifacts = st.tabs(
        ["Overview", "Red Team", "Blue Team", "Green Team", "Compliance", "Visual Evidence", "Artifacts"]
    )

    with tab_overview:
        report_download_panel(st.session_state.report_outputs)
        section_title("Recommended Controls")
        for item in results.get("recommendations", []):
            st.markdown(f"- {item}")
        st.json({
            "institution": results.get("report_context", {}).get("institution_name"),
            "report_date": results.get("report_context", {}).get("report_generated_date"),
            "audit_id": results.get("audit_id"),
            "timestamp": results.get("timestamp"),
        })

    with tab_red:
        red_results = raw.get("red_team", {}).get("results", {})
        if red_results:
            rows = []
            for attack_type, data in red_results.items():
                rows.append(
                    {
                        "attack_type": attack_type,
                        "attempts": data.get("total_attempts", 0),
                        "successful": data.get("successful_attacks", 0),
                        "success_rate": round(data.get("success_rate", 0) * 100, 1),
                    }
                )
            red_df = pd.DataFrame(rows)
            st.dataframe(red_df, use_container_width=True, hide_index=True)
            st.bar_chart(red_df.set_index("attack_type")["success_rate"])
        else:
            st.info("Run an audit to view red-team details.")

    with tab_blue:
        blue = raw.get("blue_team", {})
        if blue:
            bc1, bc2 = st.columns(2)
            bc1.metric("Threat Count", blue.get("threat_count", 0))
            blue_risk = str(blue.get("risk_level", "LOW")).upper()
            bc2.metric("Risk Level", blue_risk)
            anomalies = blue.get("anomalies", []) or blue.get("detected_anomalies", [])
            section_title("Detected Anomalies")
            if anomalies:
                for anomaly in anomalies:
                    st.markdown(f"- {anomaly}")
            else:
                st.info("No anomalies recorded.")
            section_title("Raw Blue Team Output")
            st.json(blue)
        else:
            st.info("Run an audit to view blue-team threat detection details.")

    with tab_green:
        green_items = raw.get("green_team", [])
        if green_items:
            section_title("Remediation Actions")
            for item in green_items:
                if isinstance(item, dict):
                    status = str(item.get("status", "pending")).lower()
                    badge_class = "status-fixed" if status in ("fixed", "applied", "success", "completed") else ("status-failed" if status in ("failed", "error") else "status-pending")
                    action = item.get("action", item.get("description", item.get("fix", "N/A")))
                    st.markdown(
                        f"- {action} <span class='status-badge {badge_class}'>{status.upper()}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f"- {item} <span class='status-badge status-pending'>PENDING</span>", unsafe_allow_html=True)
        else:
            st.info("Run an audit to view green-team remediation actions.")

    with tab_compliance:
        compliance_raw = raw.get("compliance", {})
        st.json(compliance_raw)
        anonymization = raw.get("phi_anonymization", {})
        if anonymization:
            section_title("PHI Anonymization")
            st.json(
                {
                    "status": anonymization.get("status"),
                    "original_phi_count": anonymization.get("original_phi_count"),
                    "phi_found": anonymization.get("phi_found"),
                }
            )

    with tab_visual:
        charts = [
            ("Risk Level Chart", "risk_chart.png"),
            ("Attack Success Rate Chart", "attack_chart.png"),
            ("Compliance Dashboard", "compliance_dashboard.png"),
            ("Team Summary", "team_summary.png"),
            ("Threat Heatmap", "threat_heatmap.png"),
        ]
        reports_base = report_dir()
        rendered = 0
        for idx in range(0, len(charts), 2):
            pair = charts[idx:idx + 2]
            cols = st.columns(2)
            for col_idx, (title, filename) in enumerate(pair):
                chart_path = reports_base / filename
                if chart_path.exists():
                    with cols[col_idx]:
                        st.caption(title)
                        st.image(str(chart_path), use_container_width=True)
                    rendered += 1
                else:
                    with cols[col_idx]:
                        st.info(f"{title} not yet generated ({filename}).")
        if rendered == 0:
            st.info("No visual evidence charts found. Run an audit and generate reports to populate this tab.")

    with tab_artifacts:
        artifacts = list_artifacts()
        if artifacts.empty:
            st.info("No generated artifacts found yet.")
        else:
            st.divider()
            st.subheader("All Generated Files")
            st.dataframe(artifacts, use_container_width=True, hide_index=True)
            selected_artifact = st.selectbox("Download any artifact", artifacts["path"].tolist())
            download_button(selected_artifact)
else:
    st.markdown(
        """
        <div class="empty-panel">
          <strong>Ready for audit.</strong><br>
          Use the sidebar to run the full workflow. Generated reports, logs, test data,
          and Kaggle packaging will be written under <code>medsec_sandbox</code>.
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("Dataset Preview", expanded=False):
    if patients:
        st.dataframe(pd.DataFrame(patients).head(25), use_container_width=True)
    else:
        st.warning("No patient data loaded.")

with st.expander("Payload Preview", expanded=False):
    if not payloads.empty:
        st.dataframe(payloads.head(25), use_container_width=True)
    else:
        st.warning("No payload data loaded.")

st.markdown(
    """
    <div class="footer-band">
      <strong>Med-Sec Audit Agent</strong> &nbsp;|&nbsp; PHI Guardians &nbsp;|&nbsp; Confidential
    </div>
    """,
    unsafe_allow_html=True,
)
