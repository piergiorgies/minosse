import asyncio
import schedule
import time

from src.config_check import check_config_version
from src.submissions_manager import start_listen_for_submissions

async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(0.1)

async def main():
    # Schedule the config version checker
    schedule.every(5).seconds.do(check_config_version)

    # Run both the scheduler and submission listener concurrently
    await asyncio.gather(
        run_scheduler(),
        start_listen_for_submissions()
    )

if __name__ == "__main__":
    try:
        # Start the asyncio event loop
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted")