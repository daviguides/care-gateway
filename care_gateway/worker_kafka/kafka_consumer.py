# caregateway/workers/kafka_consumer.py

import asyncio
from aiokafka import AIOKafkaConsumer

from care_gateway.worker_kafka.app import handle_kafka_event


async def consume_kafka_events() -> None:
    consumer = AIOKafkaConsumer(
        "edi-file-events",
        bootstrap_servers="localhost:9092",
        group_id="edi-processor",
        enable_auto_commit=True,
        auto_offset_reset="earliest",
    )

    await consumer.start()
    try:
        async for msg in consumer:
            key = msg.value.decode("utf-8")
            await handle_kafka_event(key)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume_kafka_events())
