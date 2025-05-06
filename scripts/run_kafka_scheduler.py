import logging
import asyncio
from care_gateway.worker_kafka.kafka_consumer import consume_kafka_events

from care_gateway.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    try:
        logger.info("🎯 Starting EDI file event consumer...")
        asyncio.run(consume_kafka_events())
    except KeyboardInterrupt:
        logger.info("🛑 Stopped by user.")


if __name__ == "__main__":
    main()
