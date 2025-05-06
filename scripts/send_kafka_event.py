import logging
import asyncio
import json

from aiokafka import AIOKafkaProducer

from care_gateway.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


async def send_event(filename: str) -> None:
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    try:
        event = {"s3_key": filename}
        await producer.send_and_wait(
            "edi-file-events",
            json.dumps(event).encode("utf-8"),
        )
        logger.info(f"✅ Sent event for file: {filename}")
    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(send_event("new_file_001.txt"))
