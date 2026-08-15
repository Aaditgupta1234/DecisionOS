"""HTML Rendering Engine producing styled, responsive standalone HTML documents."""

import logging
from typing import Optional
from app.reporting.constants import (
    ACCENT_COLOR_HEX,
    BG_LIGHT_HEX,
    BORDER_COLOR_HEX,
    DANGER_COLOR_HEX,
    MUTED_COLOR_HEX,
    PRIMARY_COLOR_HEX,
    SECONDARY_COLOR_HEX,
    TEXT_COLOR_HEX,
    WARNING_COLOR_HEX,
)
from app.reporting.report_templates import ReportDocument, ReportSection

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """
    Renders a structured ReportDocument into clean, responsive HTML with print-ready CSS.
    """

    @classmethod
    def render(cls, document: ReportDocument, output_path: Optional[str] = None) -> str:
        """
        Renders ReportDocument into standalone HTML string.
        """
        meta = document.metadata
        status_color = ACCENT_COLOR_HEX if meta.business_health_score >= 80 else (
            WARNING_COLOR_HEX if meta.business_health_score >= 60 else DANGER_COLOR_HEX
        )

        sections_html = []
        for s in document.sections:
            sections_html.append(cls._render_section(s))

        evidence_html = cls._render_evidence(document.evidence_references)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta.title} — DecisionOS</title>
  <style>
    :root {{
      --primary: {PRIMARY_COLOR_HEX};
      --secondary: {SECONDARY_COLOR_HEX};
      --text: {TEXT_COLOR_HEX};
      --muted: {MUTED_COLOR_HEX};
      --bg-light: {BG_LIGHT_HEX};
      --border: {BORDER_COLOR_HEX};
      --status: {status_color};
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: var(--text);
      background-color: #F1F5F9;
      margin: 0;
      padding: 40px 20px;
      line-height: 1.6;
    }}
    .document-container {{
      max-width: 850px;
      margin: 0 auto;
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
      padding: 48px;
    }}
    .cover-header {{
      border-bottom: 2px solid var(--border);
      padding-bottom: 24px;
      margin-bottom: 32px;
    }}
    .company-name {{
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--secondary);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    .document-title {{
      font-size: 2rem;
      font-weight: 800;
      color: var(--primary);
      margin: 8px 0;
      line-height: 1.25;
    }}
    .document-subtitle {{
      font-size: 1rem;
      color: var(--muted);
      margin-bottom: 24px;
    }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      background: var(--bg-light);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 16px;
      margin-top: 16px;
    }}
    .meta-item label {{
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      display: block;
    }}
    .meta-item span {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--primary);
    }}
    .status-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      color: #FFFFFF;
      background-color: var(--status);
      font-size: 0.85rem;
    }}
    .section-block {{
      margin-top: 36px;
      page-break-inside: avoid;
    }}
    .section-title {{
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--primary);
      border-bottom: 1px solid var(--border);
      padding-bottom: 8px;
      margin-bottom: 16px;
    }}
    .callout-box {{
      background: var(--bg-light);
      border-left: 4px solid var(--secondary);
      border-radius: 4px;
      padding: 14px 18px;
      margin-bottom: 16px;
      font-weight: 600;
      font-size: 0.95rem;
      color: var(--primary);
    }}
    .table-container {{
      overflow-x: auto;
      margin: 16px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }}
    th {{
      background: var(--primary);
      color: #FFFFFF;
      text-align: left;
      padding: 10px 12px;
      font-weight: 600;
    }}
    td {{
      padding: 8px 12px;
      border-bottom: 1px solid var(--border);
    }}
    tr:nth-child(even) td {{
      background: var(--bg-light);
    }}
    .footer-note {{
      margin-top: 48px;
      border-top: 1px solid var(--border);
      padding-top: 16px;
      font-size: 0.75rem;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
    }}
    @media print {{
      body {{
        background: transparent;
        padding: 0;
      }}
      .document-container {{
        box-shadow: none;
        border: none;
        padding: 0;
      }}
    }}
  </style>
</head>
<body>
  <div class="document-container">
    <div class="cover-header">
      <div class="company-name">{meta.company_name}</div>
      <h1 class="document-title">{meta.title}</h1>
      <div class="document-subtitle">{meta.subtitle or "Deterministic Business Telemetry & Executive Briefing"}</div>
      
      <div class="meta-grid">
        <div class="meta-item">
          <label>Dataset</label>
          <span>{meta.dataset_name}</span>
        </div>
        <div class="meta-item">
          <label>Business Health</label>
          <span class="status-badge">{meta.business_health_score}/100 ({meta.business_health_status})</span>
        </div>
        <div class="meta-item">
          <label>Generated Date</label>
          <span>{meta.generated_at}</span>
        </div>
        <div class="meta-item">
          <label>Platform Engine</label>
          <span>{meta.decisionos_version}</span>
        </div>
      </div>
    </div>

    {''.join(sections_html)}

    {evidence_html}

    <div class="footer-note">
      <span>DecisionOS Explainable AI SaaS Platform — Boardroom Confidential</span>
      <span>Document Template v{meta.template_version}</span>
    </div>
  </div>
</body>
</html>"""

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

        return html_content

    @classmethod
    def _render_section(cls, section: ReportSection) -> str:
        callout_block = f'<div class="callout-box">💡 <b>Key Takeaway:</b> {section.callout}</div>' if section.callout else ""
        content_p = f'<p>{section.content}</p>' if section.content else ""
        table_html = cls._render_data_table(section.data) if section.data else ""

        return f"""
        <div class="section-block">
          <h2 class="section-title">{section.title}</h2>
          {callout_block}
          {content_p}
          {table_html}
        </div>
        """

    @classmethod
    def _render_data_table(cls, data: dict) -> str:
        if "metrics_table" in data and data["metrics_table"]:
            rows = []
            for item in data["metrics_table"][:12]:
                rows.append(f"<tr><td><b>{item.get('metric_name')}</b></td><td>{item.get('category')}</td><td>{item.get('value')}</td></tr>")
            return f"""<div class="table-container"><table>
              <thead><tr><th>Metric Name</th><th>Category</th><th>Current Value</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table></div>"""

        if "findings_table" in data and data["findings_table"]:
            rows = []
            for item in data["findings_table"][:8]:
                rows.append(f"<tr><td><b>{item.get('title')}</b></td><td><span class='badge'>{item.get('severity')}</span></td><td>{item.get('impact')}</td><td>{item.get('confidence')}</td></tr>")
            return f"""<div class="table-container"><table>
              <thead><tr><th>Diagnostic Finding</th><th>Severity</th><th>Business Impact</th><th>Confidence</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table></div>"""

        if "root_causes_table" in data and data["root_causes_table"]:
            rows = []
            for item in data["root_causes_table"][:6]:
                rows.append(f"<tr><td><b>{item.get('cause')}</b></td><td>{item.get('effect')}</td><td>{item.get('strength')}</td><td>{item.get('impact_score')}</td></tr>")
            return f"""<div class="table-container"><table>
              <thead><tr><th>Root Cause Driver</th><th>Impacted Symptom</th><th>Strength</th><th>Impact Score</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table></div>"""

        if "recommendations_table" in data and data["recommendations_table"]:
            rows = []
            for item in data["recommendations_table"][:8]:
                rows.append(f"<tr><td><b>{item.get('title')}</b></td><td>{item.get('priority')}</td><td>{item.get('impact')}</td><td>{item.get('effort')}</td></tr>")
            return f"""<div class="table-container"><table>
              <thead><tr><th>Strategic Recommendation</th><th>Priority</th><th>Impact</th><th>Effort</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table></div>"""

        if "forecasts_table" in data and data["forecasts_table"]:
            rows = []
            for item in data["forecasts_table"][:6]:
                rows.append(f"<tr><td><b>{item.get('metric_key')}</b></td><td>{item.get('model_type')}</td><td>{item.get('mape')}</td><td>{item.get('periods')}</td></tr>")
            return f"""<div class="table-container"><table>
              <thead><tr><th>Metric</th><th>Model Type</th><th>MAPE</th><th>Periods</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table></div>"""

        if "scenarios_table" in data and data["scenarios_table"]:
            rows = []
            for item in data["scenarios_table"][:6]:
                rows.append(f"<tr><td><b>{item.get('name')}</b></td><td>{item.get('status')}</td><td>{item.get('assumptions_count')}</td></tr>")
            return f"""<div class="table-container"><table>
              <thead><tr><th>Scenario Name</th><th>Status</th><th>Assumptions</th></tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table></div>"""

        return ""

    @classmethod
    def _render_evidence(cls, evidence: list) -> str:
        if not evidence:
            return ""
        rows = []
        for ev in evidence[:10]:
            title = ev.get("title") or ev.get("metric_key") or ev.get("name") or ""
            rows.append(f"<tr><td><code>{ev.get('id')}</code></td><td>{ev.get('type')}</td><td>{title}</td></tr>")
        return f"""
        <div class="section-block">
          <h2 class="section-title">Appendix: Evidence References & Verification Traceability</h2>
          <p>All statements trace to verified platform artifacts and deterministic analytical engine outputs.</p>
          <div class="table-container"><table>
            <thead><tr><th>Artifact UUID</th><th>Type</th><th>Title / Key</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table></div>
        </div>
        """
