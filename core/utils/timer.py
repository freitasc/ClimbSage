from datetime import datetime, timedelta
from core.utils.logger import debug_logger, time_logger
import os

class GlobalTimer:
    _start_time = None
    _markdown_file = "TIMES.md"

    @classmethod
    def start(cls):
        cls._start_time = datetime.now()
        debug_logger.debug("Timer started")

    @classmethod
    def stop(cls, description: str = ""):
        if cls._start_time is None:
            debug_logger.warning("Timer stopped without being started")
            return

        end_time = datetime.now()
        elapsed = end_time - cls._start_time
        cls._start_time = None

        time_logger.info(
            f"{description} - Elapsed: {elapsed.total_seconds():.2f}s"
        )
        cls._log_to_markdown(description, end_time, elapsed)
        debug_logger.debug(f"Timer stopped - {description}")

    @classmethod
    def _log_to_markdown(cls, description: str, end_time: datetime, elapsed: timedelta):
        os.makedirs("logs", exist_ok=True)
        filepath = f"logs/{cls._markdown_file}"

        entry = (
            f"| {description} | "
            f"{end_time.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{elapsed.total_seconds():.2f}s |\n"
        )

        try:
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write("# Execution Times\n\n")
                    f.write("| Description | End Time | Elapsed |\n")
                    f.write("|-------------|----------|---------|\n")

            with open(filepath, 'a') as f:
                f.write(entry)
        except Exception as e:
            debug_logger.error(f"Failed to write to markdown file: {str(e)}")