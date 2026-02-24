import json
import sys
from pathlib import Path


def main(alerts_json: str, mode: str) -> None:
    alerts = json.loads(Path(alerts_json).read_text())
    n_alerts = int(alerts.get("n_alerts", 0))
    ok = bool(alerts.get("ok", False))
    errors = alerts.get("errors", [])

    #Fail on scan errors
    if not ok or errors:
        print(f"[gate] FAIL: scan error(s): {errors[:1]}")
        sys.exit(1)

    if mode.lower() == "fail" and n_alerts > 0:
        print(f"[gate] FAIL: {n_alerts} alerts found (mode=fail)")
        sys.exit(1)

    print(f"[gate] PASS: ok={ok}, alerts={n_alerts}, mode={mode}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: gate.py <alerts.json> <pass|fail>")
    main(sys.argv[1], sys.argv[2])
