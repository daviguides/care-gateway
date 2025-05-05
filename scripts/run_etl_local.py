import asyncio
from care_gateway.worker_kafka.edi_etl.tasks import run_edi_etl

if __name__ == "__main__":
    asyncio.run(run_edi_etl())
