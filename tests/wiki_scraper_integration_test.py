from scraper import Scraper
import sys


def run_get_summary_integration_test():
    scraper = Scraper(mode='offline', source='../offline_wiki', phrase="creeper")
    proper_result = (
        "A creeper is a common hostile mob that quietly approaches a player, hisses, "
        "and if not retreated from in time, will explode. Creeper explosions can destroy "
        "blocks and deal massive amounts of damage, which can be completely "
        "blocked using a shield."
    )
    assert scraper.get_summary() == proper_result, "Expected different get_summary result for creeper"


if __name__ == "__main__":
    try:
        print("Running integration test")
        run_get_summary_integration_test()
        print("Test passed! ;))")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Encountered exception: {e}")
        sys.exit(2)
