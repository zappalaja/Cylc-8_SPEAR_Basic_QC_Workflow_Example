import json
import sys
from pathlib import Path
from datetime import datetime
import yaml


def main(cfg_path: str, meta_path: str, alerts_path: str, out_report: str) -> None:
    cfg = yaml.safe_load(Path(cfg_path).read_text())
    meta = json.loads(Path(meta_path).read_text())
    alerts = json.loads(Path(alerts_path).read_text())

    lines = []
    lines.append("SPEAR PRECIP QC REPORT")
    lines.append("======================")
    lines.append("")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append(f"Input file: {cfg['input_file']}")
    lines.append(f"Variable: {cfg['variable_name']}")
    lines.append(f"Threshold (mm/6-hr): {cfg['threshold_mm_6hr']}")
    lines.append("")

    lines.append("Metadata QC:")
    lines.append(f"  PASS: {meta.get('ok', False)}")
    if not meta.get("ok", False):
        for e in meta.get("errors", []):
            lines.append(f"  - {e}")
    else:
        lines.append(f"  n_timesteps: {meta.get('n_timesteps')}")
        lines.append(f"  var_shape: {meta.get('var_shape')}")
        lines.append(f"  time_units: {meta.get('time_units')}")
        lines.append("")

    lines.append("Rogue Pixel Scan:")
    lines.append(f"  PASS: {alerts.get('ok', False)}")
    lines.append(f"  duration_sec: {alerts.get('duration_sec'):.2f}")
    lines.append(f"  n_alerts: {alerts.get('n_alerts')}")
    if alerts.get("errors"):
        for e in alerts["errors"]:
            lines.append(f"  - ERROR: {e}")
    lines.append("")

    if alerts.get("n_alerts", 0) > 0:
        lines.append("Alerts (timestep-level):")
        for a in alerts["alerts"][:50]:
            lines.append(f"  - t={a['t_index']:05d} time={a['time_str']} max_mm6hr={a['max_mm_6hr']:.2f}")
            lines.append(f"    plot: {a['plot_file']}")
        if alerts["n_alerts"] > 50:
            lines.append(f"  (showing first 50 of {alerts['n_alerts']})")
        lines.append("")

    Path(out_report).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("Usage: summarize.py <config.yaml> <metadata.json> <alerts.json> <report.txt>")
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
