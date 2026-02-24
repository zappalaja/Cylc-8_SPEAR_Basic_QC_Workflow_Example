import json
import sys
from pathlib import Path

import netCDF4
import yaml


def main(cfg_path: str, out_json: str) -> None:
    cfg = yaml.safe_load(Path(cfg_path).read_text())
    fp = cfg["input_file"]
    var = cfg["variable_name"]
    lat = cfg["lat_dim"]
    lon = cfg["lon_dim"]
    tdim = cfg["time_dim"]

    meta = {"input_file": fp, "checks": {}, "ok": True, "errors": []}

    try:
        with netCDF4.Dataset(fp, "r") as ds:
            meta["dimensions"] = list(ds.dimensions.keys())
            meta["variables"] = list(ds.variables.keys())

            for name in (var, lat, lon, tdim):
                exists = name in ds.variables
                meta["checks"][f"var_exists:{name}"] = exists
                if not exists:
                    meta["ok"] = False
                    meta["errors"].append(f"Missing variable: {name}")

            if meta["ok"]:
                v = ds.variables[var]
                meta["var_shape"] = list(getattr(v, "shape", []))
                meta["var_dtype"] = str(getattr(v, "dtype", ""))

                time_var = ds.variables[tdim]
                meta["n_timesteps"] = int(len(time_var))
                meta["time_units"] = getattr(time_var, "units", None)
                meta["time_calendar"] = getattr(time_var, "calendar", "standard")

                #Validity  checks (for personal logging)
                meta["checks"]["time_len_positive"] = meta["n_timesteps"] > 0
                meta["checks"]["pr_has_3_dims"] = (len(meta["var_shape"]) == 3)

                if not meta["checks"]["time_len_positive"]:
                    meta["ok"] = False
                    meta["errors"].append("Time dimension length is not positive")
                if not meta["checks"]["pr_has_3_dims"]:
                    meta["ok"] = False
                    meta["errors"].append(f"Expected 3D var (time,lat,lon) but got shape {meta['var_shape']}")

    except Exception as e:
        meta["ok"] = False
        meta["errors"].append(str(e))

    Path(out_json).write_text(json.dumps(meta, indent=2))
    if not meta["ok"]:
        print("METADATA_QC: FAIL")
        for err in meta["errors"]:
            print(" -", err)
        sys.exit(1)

    print("METADATA_QC: PASS")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: metadata_qc.py <config.yaml> <out.json>")
    main(sys.argv[1], sys.argv[2])
