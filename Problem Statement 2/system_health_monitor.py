#!/usr/bin/env python3
"""
System Health Monitoring Script
Monitors CPU, memory, disk, and processes — alerts when thresholds are exceeded.
"""

import os
import sys
import logging
import datetime
import subprocess
import shutil

# ── Try to import psutil; install if missing ──────────────────────────────────
try:
    import psutil
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "psutil", "--break-system-packages", "-q"])
    import psutil

# ─────────────────────────────────────────────────────────────────────────────
# Thresholds (%)
# ─────────────────────────────────────────────────────────────────────────────
THRESHOLDS = {
    "cpu_percent":    80.0,   # CPU usage %
    "memory_percent": 80.0,   # RAM usage %
    "disk_percent":   85.0,   # Disk usage %
    "top_n_processes": 5,     # How many top processes to report
}

LOG_FILE = "/home/claude/system_health.log"

# ─────────────────────────────────────────────────────────────────────────────
# Logging setup
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

SEPARATOR = "=" * 62


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _status(value: float, threshold: float) -> str:
    return "⚠  ALERT" if value >= threshold else "✓  OK"


# ─────────────────────────────────────────────────────────────────────────────
# Check functions
# ─────────────────────────────────────────────────────────────────────────────
def check_cpu() -> dict:
    """Return CPU metrics; alert if above threshold."""
    # interval=1 gives a meaningful reading (not 0.0)
    percent = psutil.cpu_percent(interval=1)
    count_logical = psutil.cpu_count(logical=True)
    count_physical = psutil.cpu_count(logical=False)
    freq = psutil.cpu_freq()

    alert = percent >= THRESHOLDS["cpu_percent"]
    return {
        "percent": percent,
        "logical_cores": count_logical,
        "physical_cores": count_physical,
        "freq_mhz": round(freq.current, 1) if freq else "N/A",
        "alert": alert,
    }


def check_memory() -> dict:
    """Return RAM + swap metrics; alert if above threshold."""
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    alert = vm.percent >= THRESHOLDS["memory_percent"]
    return {
        "total": vm.total,
        "used": vm.used,
        "available": vm.available,
        "percent": vm.percent,
        "swap_total": sw.total,
        "swap_used": sw.used,
        "swap_percent": sw.percent,
        "alert": alert,
    }


def check_disk() -> list[dict]:
    """Return per-partition disk metrics; alert partitions over threshold."""
    results = []
    seen = set()
    for part in psutil.disk_partitions(all=False):
        if part.mountpoint in seen:
            continue
        seen.add(part.mountpoint)
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        alert = usage.percent >= THRESHOLDS["disk_percent"]
        results.append({
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.percent,
            "alert": alert,
        })
    return results


def check_processes() -> list[dict]:
    """Return the top-N processes by CPU usage."""
    procs = []
    for p in psutil.process_iter(["pid", "name", "username",
                                   "cpu_percent", "memory_percent",
                                   "status"]):
        try:
            info = p.info
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # A second pass to get meaningful cpu_percent (needs two samples)
    # We already called cpu_percent(interval=1) for system CPU above,
    # so process-level values are now populated.
    procs.sort(key=lambda x: x.get("cpu_percent") or 0, reverse=True)
    return procs[: THRESHOLDS["top_n_processes"]]


# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────
def run_report() -> bool:
    """Run all checks, log results, return True if any alert fired."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    any_alert = False

    log.info(SEPARATOR)
    log.info("  SYSTEM HEALTH REPORT  —  %s", now)
    log.info(SEPARATOR)

    # ── CPU ─────────────────────────────────────────────────────────────────
    cpu = check_cpu()
    status = _status(cpu["percent"], THRESHOLDS["cpu_percent"])
    log.info("CPU Usage   : %5.1f%%   [threshold: %g%%]  %s",
             cpu["percent"], THRESHOLDS["cpu_percent"], status)
    log.info("  Cores     : %d physical / %d logical",
             cpu["physical_cores"], cpu["logical_cores"])
    log.info("  Frequency : %s MHz", cpu["freq_mhz"])
    if cpu["alert"]:
        any_alert = True
        log.warning("  >>> CPU usage exceeded threshold! (%.1f%% >= %g%%)",
                    cpu["percent"], THRESHOLDS["cpu_percent"])

    log.info("")

    # ── Memory ──────────────────────────────────────────────────────────────
    mem = check_memory()
    status = _status(mem["percent"], THRESHOLDS["memory_percent"])
    log.info("Memory      : %5.1f%%   [threshold: %g%%]  %s",
             mem["percent"], THRESHOLDS["memory_percent"], status)
    log.info("  Total     : %s", _fmt_bytes(mem["total"]))
    log.info("  Used      : %s", _fmt_bytes(mem["used"]))
    log.info("  Available : %s", _fmt_bytes(mem["available"]))
    log.info("  Swap Used : %s / %s  (%.1f%%)",
             _fmt_bytes(mem["swap_used"]),
             _fmt_bytes(mem["swap_total"]),
             mem["swap_percent"])
    if mem["alert"]:
        any_alert = True
        log.warning("  >>> Memory usage exceeded threshold! (%.1f%% >= %g%%)",
                    mem["percent"], THRESHOLDS["memory_percent"])

    log.info("")

    # ── Disk ────────────────────────────────────────────────────────────────
    disks = check_disk()
    log.info("Disk Partitions (%d found):", len(disks))
    for d in disks:
        status = _status(d["percent"], THRESHOLDS["disk_percent"])
        log.info("  %-20s  %5.1f%%  [threshold: %g%%]  %s",
                 d["mountpoint"], d["percent"],
                 THRESHOLDS["disk_percent"], status)
        log.info("    Device: %-12s  FS: %-8s  Total: %s  Free: %s",
                 d["device"], d["fstype"],
                 _fmt_bytes(d["total"]), _fmt_bytes(d["free"]))
        if d["alert"]:
            any_alert = True
            log.warning("    >>> Disk usage on '%s' exceeded threshold! "
                        "(%.1f%% >= %g%%)",
                        d["mountpoint"], d["percent"],
                        THRESHOLDS["disk_percent"])

    log.info("")

    # ── Top Processes ────────────────────────────────────────────────────────
    procs = check_processes()
    log.info("Top %d Processes by CPU%%:", THRESHOLDS["top_n_processes"])
    log.info("  %-8s  %-25s  %-12s  %7s  %7s  %s",
             "PID", "Name", "User", "CPU%", "MEM%", "Status")
    log.info("  " + "-" * 70)
    for p in procs:
        log.info("  %-8s  %-25s  %-12s  %6.1f%%  %6.1f%%  %s",
                 p.get("pid", "?"),
                 (p.get("name") or "")[:25],
                 (p.get("username") or "")[:12],
                 p.get("cpu_percent") or 0.0,
                 p.get("memory_percent") or 0.0,
                 p.get("status", ""))

    log.info("")
    log.info(SEPARATOR)

    if any_alert:
        log.warning("SUMMARY: ⚠  One or more metrics exceeded their thresholds.")
    else:
        log.info("SUMMARY: ✓  All metrics are within normal limits.")

    log.info(SEPARATOR)
    return any_alert


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    alert_fired = run_report()
    log.info("Log saved to: %s", LOG_FILE)
    sys.exit(1 if alert_fired else 0)
