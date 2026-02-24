import json
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List

import netCDF4
import numpy as np
import yaml

import matplotlib
matplotlib.use("Agg")  # safer in batch/headless runs
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


def create_alert_plot(data_slice_pr: np.ndarray, lons: np.ndarray, lats: np.ndarray,
                      date_obj: Any, out_path: Path, title: str,
                      cmap: str, dpi: int, fig_size: List[int]) -> None:
    precip_total_mm = data_slice_pr * 21600.0
    fig = plt.figure(figsize=tuple(fig_size))
    try:
        ax = plt.axes(projection=ccrs.Robinson())
        ax.set_global()
        mesh = ax.pcolormesh(
            lons, lats, precip_total_mm,
            transform=ccrs.PlateCarree(),
            cmap=cmap
        )
        ax.coastlines()
        ax.gridlines(draw_labels=False)
        cbar = plt.colorbar(mesh, orientation="vertical", pad=0.02, aspect=30, shrink=0.8)
        cbar.set_label("Precipitation (mm/6-hr)")

        start_time = date_obj
        end_time = start_time + timedelta(hours=6)
        ax.set_title(
            f"{title}\n{start_time.strftime('%Y-%m-%d %H:%M')}–{end_time.strftime('%H:%M')}",
            pad=20
        )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=dpi, bbox_inches="tight")
    finally:
        plt.close(fig)


def main(cfg_path: str, out_json: str) -> None:
    cfg = yaml.safe_load(Path(cfg_path).read_text())

    fp = cfg["input_file"]
    var = cfg["variable_name"]
    lat = cfg["lat_dim"]
    lon = cfg["lon_dim"]
    tdim = cfg["time_dim"]
    thr = float(cfg["threshold_mm_6hr"])
    out_dir = Path(cfg["output_directory"])
    plot_cfg: Dict[str, Any] = cfg.get("plot_settings", {})
    out_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    alerts: List[Dict[str, Any]] = []
    errors: List[str] = []

    # Open ONCE, scan sequentially (stable, avoids HDF5 concurrency issues)
    try:
        with netCDF4.Dataset(fp, "r") as ds:
            if var not in ds.variables:
                raise RuntimeError(f"Variable '{var}' not found")
            if lat not in ds.variables or lon not in ds.variables or tdim not in ds.variables:
                raise RuntimeError(f"Missing one of dims/vars: {lat}, {lon}, {tdim}")

            pr = ds.variables[var]
            lats = np.array(ds.variables[lat][:])
            lons = np.array(ds.variables[lon][:])
            tv = ds.variables[tdim]
            n = len(tv)

            # Optional: cap plots for demos to avoid generating thousands
            max_plots = int(cfg.get("max_plots", 50))

            for t_index in range(n):
                data_slice = pr[t_index, :, :]  # may be masked
                total_mm6hr = data_slice * 21600.0

                # use masked-aware max/any
                if np.ma.any(total_mm6hr > thr):
                    max_val = float(np.ma.max(total_mm6hr))
                    date_obj = netCDF4.num2date(
                        tv[t_index], tv.units, getattr(tv, "calendar", "standard")
                    )

                    basename = Path(fp).name.replace(".nc", "")
                    plot_file = f"ALERT_{basename}_timestep_{t_index:05d}.png"
                    plot_path = out_dir / plot_file

                    # Generate plot (but cap how many we make)
                    if len(alerts) < max_plots:
                        create_alert_plot(
                            np.array(data_slice),
                            lons, lats,
                            date_obj,
                            plot_path,
                            title=f"High Precipitation Found: {Path(fp).name}",
                            cmap=plot_cfg.get("cmap", "viridis"),
                            dpi=int(plot_cfg.get("dpi", 150)),
                            fig_size=plot_cfg.get("figure_size", [12, 6]),
                        )

                    alerts.append({
                        "t_index": t_index,
                        "time_str": str(date_obj),
                        "max_mm_6hr": max_val,
                        "plot_file": str(plot_path) if len(alerts) <= max_plots else "(plot skipped: max_plots cap)",
                    })

    except Exception as e:
        errors.append(str(e))

    duration = time.time() - start
    out = {
        "input_file": fp,
        "threshold_mm_6hr": thr,
        "n_alerts": len(alerts),
        "alerts": alerts,
        "errors": errors,
        "duration_sec": duration,
        "ok": (len(errors) == 0),
    }
    Path(out_json).write_text(json.dumps(out, indent=2))
    print(f"[scan_rogue_pixels] completed in {duration:.2f}s, alerts={len(alerts)}")

    if errors:
        print("[scan_rogue_pixels] ERROR:", errors[0])
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: scan_rogue_pixels.py <config.yaml> <out.json>")
    main(sys.argv[1], sys.argv[2])
