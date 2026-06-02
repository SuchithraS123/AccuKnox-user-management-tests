#!/usr/bin/env python3
"""
Application Health Checker
Checks HTTP/HTTPS endpoints and reports whether each app is UP or DOWN.
Supports custom expected status codes, timeouts, keyword checks, and retries.
"""

import sys
import time
import logging
import datetime
import subprocess

# ── Try to import requests; install if missing ────────────────────────────────
try:
    import requests
    from requests.exceptions import (
        ConnectionError, Timeout, TooManyRedirects, RequestException
    )
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "requests", "--break-system-packages", "-q"])
    import requests
    from requests.exceptions import (
        ConnectionError, Timeout, TooManyRedirects, RequestException
    )

# ─────────────────────────────────────────────────────────────────────────────
# Configuration — edit the APPS list to add / remove targets
# ─────────────────────────────────────────────────────────────────────────────
APPS = [
    {
        "name":             "Google",
        "url":              "https://www.google.com",
        "expected_status":  [200],
        "keyword":          None,          # Optional: string that must appear in body
        "timeout":          5,             # seconds
        "retries":          2,
    },
    {
        "name":             "GitHub",
        "url":              "https://github.com",
        "expected_status":  [200],
        "keyword":          "GitHub",
        "timeout":          5,
        "retries":          2,
    },
    {
        "name":             "httpbin (200 OK)",
        "url":              "https://httpbin.org/status/200",
        "expected_status":  [200],
        "keyword":          None,
        "timeout":          5,
        "retries":          2,
    },
    {
        "name":             "httpbin (503 – simulated outage)",
        "url":              "https://httpbin.org/status/503",
        "expected_status":  [200],         # We expect 200 but will get 503 → DOWN
        "keyword":          None,
        "timeout":          5,
        "retries":          1,
    },
    {
        "name":             "Non-existent host (DOWN)",
        "url":              "https://this-host-does-not-exist.example.invalid",
        "expected_status":  [200],
        "keyword":          None,
        "timeout":          4,
        "retries":          1,
    },
]

LOG_FILE = "/home/claude/app_health.log"
REQUEST_HEADERS = {
    "User-Agent": "AppHealthChecker/1.0 (Python)"
}

# ─────────────────────────────────────────────────────────────────────────────
# Logging
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

SEPARATOR = "=" * 66


# ─────────────────────────────────────────────────────────────────────────────
# Core check
# ─────────────────────────────────────────────────────────────────────────────
def check_app(app: dict) -> dict:
    """
    Probe a single endpoint; retry on failure.
    Returns a result dict with status, http_code, latency_ms, and reason.
    """
    name      = app["name"]
    url       = app["url"]
    expected  = app.get("expected_status", [200])
    keyword   = app.get("keyword")
    timeout   = app.get("timeout", 5)
    retries   = app.get("retries", 2)

    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            t0 = time.monotonic()
            resp = requests.get(
                url,
                timeout=timeout,
                headers=REQUEST_HEADERS,
                allow_redirects=True,
            )
            latency_ms = round((time.monotonic() - t0) * 1000, 1)

            # Status-code check
            if resp.status_code not in expected:
                last_error = (
                    f"HTTP {resp.status_code} "
                    f"(expected {expected})"
                )
                # short back-off before retry
                if attempt < retries:
                    time.sleep(1)
                continue

            # Optional keyword check
            if keyword and keyword.lower() not in resp.text.lower():
                last_error = (
                    f"Keyword '{keyword}' not found in response body"
                )
                if attempt < retries:
                    time.sleep(1)
                continue

            # All checks passed → UP
            return {
                "name":        name,
                "url":         url,
                "status":      "UP",
                "http_code":   resp.status_code,
                "latency_ms":  latency_ms,
                "reason":      "All checks passed",
                "attempts":    attempt,
            }

        except Timeout:
            last_error = f"Timed out after {timeout}s"
        except ConnectionError as exc:
            last_error = f"Connection error — {exc}"
        except TooManyRedirects:
            last_error = "Too many redirects"
        except RequestException as exc:
            last_error = f"Request failed — {exc}"

        if attempt < retries:
            time.sleep(1)

    # All attempts exhausted
    return {
        "name":       name,
        "url":        url,
        "status":     "DOWN",
        "http_code":  None,
        "latency_ms": None,
        "reason":     last_error,
        "attempts":   retries,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────
def run_report() -> bool:
    """Check all apps, log a summary report. Returns True if any app is DOWN."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = []

    log.info(SEPARATOR)
    log.info("  APPLICATION HEALTH CHECKER  —  %s", now)
    log.info(SEPARATOR)
    log.info("Probing %d application(s) …", len(APPS))
    log.info("")

    for app in APPS:
        result = check_app(app)
        results.append(result)

        icon    = "✓ " if result["status"] == "UP" else "✗ "
        latency = (f"{result['latency_ms']} ms"
                   if result["latency_ms"] is not None else "N/A")
        http    = (str(result["http_code"])
                   if result["http_code"] is not None else "—")

        log.info(
            "%s%-35s  Status: %-4s  HTTP: %-5s  Latency: %-10s  Attempts: %d",
            icon,
            result["name"][:35],
            result["status"],
            http,
            latency,
            result["attempts"],
        )

        if result["status"] == "DOWN":
            log.warning("    Reason : %s", result["reason"])
        elif result.get("reason") != "All checks passed":
            log.info("    Reason : %s", result["reason"])

    # ── Summary ──────────────────────────────────────────────────────────────
    up_count   = sum(1 for r in results if r["status"] == "UP")
    down_count = len(results) - up_count
    any_down   = down_count > 0

    log.info("")
    log.info(SEPARATOR)
    log.info("SUMMARY: %d/%d UP   |   %d/%d DOWN",
             up_count, len(results), down_count, len(results))

    if any_down:
        log.warning("⚠  The following applications are DOWN:")
        for r in results:
            if r["status"] == "DOWN":
                log.warning("   • %s  (%s)  — %s",
                            r["name"], r["url"], r["reason"])
    else:
        log.info("✓  All applications are UP and responding correctly.")

    log.info(SEPARATOR)
    return any_down


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    any_down = run_report()
    log.info("Log saved to: %s", LOG_FILE)
    sys.exit(1 if any_down else 0)
