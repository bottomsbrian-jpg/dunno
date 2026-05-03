"""
nexus_smoke_test.py — Pre-flight checks before going live.
Run: python nexus_smoke_test.py
Exits 0 if all pass, 1 if any fail.
"""
import importlib, os, sys, socket, time

os.environ.setdefault("NEXUS_TRADING_MODE", "paper")
os.environ.setdefault("NEXUS_LIVE_CONFIRMED", "false")
import nexus_config as cfg

PASS, FAIL, WARN, SKIP = "  PASS", "  FAIL", "  WARN", "  SKIP"
results = []

def check(name, passed, detail="", warn_only=False):
    tag = PASS if passed else (WARN if warn_only else FAIL)
    results.append((name, tag, detail))
    print(f"{tag}  {name}" + (f"  [{detail}]" if detail else ""))
    return passed

major, minor = sys.version_info[:2]
check("Python version >= 3.10", major == 3 and minor >= 10, f"Found {major}.{minor}")

for var in ["NEXUS_TRADING_MODE"]:
    check(f"Env var {var} is set", bool(os.getenv(var)), os.getenv(var, "(missing)"))

for var in ["ALERT_EMAIL_ENABLED", "ALERT_WEBHOOK_ENABLED"]:
    check(f"Env var {var} is set", bool(os.getenv(var)), os.getenv(var, "not set"), warn_only=True)

if cfg.IS_LIVE:
    for var in ["NEXUS_LIVE_CONFIRMED","BINANCE_API_KEY","BINANCE_API_SECRET"]:
        check(f"Live var {var} is set", bool(os.getenv(var)))
else:
    print(f"{SKIP}  Live env var checks  [mode=paper]")

for mod in ["nexus_config","nexus_alerting","nexus_health","nexus_logging_setup"]:
    try:
        importlib.import_module(mod); check(f"Import {mod}", True)
    except Exception as e:
        check(f"Import {mod}", False, str(e))

print(f"\n  Bot module checks ({len(cfg.BOT_NAMES)} bots):")
for name in cfg.BOT_NAMES:
    try:
        mod = importlib.import_module(name)
        check(f"  Bot '{name}' has run()", callable(getattr(mod,"run",None)))
    except ModuleNotFoundError:
        check(f"  Bot '{name}' imports", False, "ModuleNotFoundError")

try:
    leader = importlib.import_module("nexus_leader")
    check("nexus_leader has run()", callable(getattr(leader,"run",None)))
except ModuleNotFoundError:
    check("nexus_leader imports", False, "ModuleNotFoundError")

print("\n  Network checks:")
for host, port in [("api.binance.com",443),("api.kraken.com",443),("api.coinbase.com",443)]:
    try:
        with socket.create_connection((host, port), timeout=5): pass
        check(f"  Network -> {host}", True)
    except OSError as e:
        check(f"  Network -> {host}", False, str(e), warn_only=True)

import urllib.request
from nexus_health import start_health_server
try:
    start_health_server(port=18080, bot_names=cfg.BOT_NAMES[:1])
    time.sleep(0.3)
    with urllib.request.urlopen("http://localhost:18080/", timeout=3) as r:
        check("Healthcheck server responds", r.status == 200)
except Exception as e:
    check("Healthcheck server responds", False, str(e))

print("\n" + "-"*50)
failed = sum(1 for _,t,_ in results if t == FAIL)
warned = sum(1 for _,t,_ in results if t == WARN)
passed = sum(1 for _,t,_ in results if t == PASS)
print(f"  {passed} passed | {warned} warnings | {failed} failed")
if failed:
    print(f"\n  {failed} check(s) FAILED — fix before going live."); sys.exit(1)
else:
    print("\n  All critical checks passed."); sys.exit(0)