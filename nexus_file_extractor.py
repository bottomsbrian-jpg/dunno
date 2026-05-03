import os
import sys

REQUIRED_FILES = [
    "nexus_runner.py", "nexus_config.py", "nexus_logging_setup.py",
    "nexus_health.py", "nexus_alerting.py", "nexus_smoke_test.py",
    "nexus_leader.py", "requirements.txt", "railway.json",
    "strategy_bot_1.py", "strategy_bot_2.py", "strategy_bot_3.py",
    "strategy_bot_4.py", "strategy_bot_5.py", "strategy_bot_6.py",
    "strategy_bot_7.py", "strategy_bot_8.py", "strategy_bot_9.py",
    "strategy_bot_10.py",
]

def check_files(directory="."):
    missing = []
    for f in REQUIRED_FILES:
        if not os.path.exists(os.path.join(directory, f)):
            missing.append(f)
    if missing:
        print(f"MISSING FILES: {missing}")
        return False
    print("All required files present.")
    return True

if __name__ == "__main__":
    check_files()
