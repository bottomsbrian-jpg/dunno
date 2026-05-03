import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("nexus.smoke_test")

def run_smoke_test():
    log.info("Running NEXUS smoke test...")
    try:
        from nexus_config import load_config
        config = load_config()
        log.info("Config loaded OK. Mode=%s", config.get("NEXUS_TRADING_MODE"))
    except Exception as e:
        log.error("Config failed: %s", e)
        return False
    bots = []
    for i in range(1, 11):
        try:
            mod = __import__(f"strategy_bot_{i}")
            bots.append(mod.__name__)
        except Exception as e:
            log.error("Bot %d failed to import: %s", i, e)
            return False
    log.info("All bots imported OK: %s", bots)
    log.info("Smoke test PASSED.")
    return True

if __name__ == "__main__":
    run_smoke_test()
