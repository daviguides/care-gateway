from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from databricksx12 import EDI
from databricksx12.hls import HealthcareManager
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name

from care_gateway.utils.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

DATA_DIR = "data"


def parse_edi_files_individually(
    files: list[str], inbox_dir: str = "inbox", out_dir: str = "out"
) -> list[dict[str, Any]]:
    """
    Parse EDI 837 files individually, save each output to a JSON file,
    and return a list of all claims as dictionaries.
    """
    spark = SparkSession.builder.appName("EDI837Parser").getOrCreate()
    sc = spark.sparkContext

    paths = [f"{DATA_DIR}/{inbox_dir}/{file}" for file in files]
    rdd = sc.wholeTextFiles(",".join(paths))
    df = rdd.toDF(["filename", "content"])

    hm = HealthcareManager()
    output_path = Path(f"{DATA_DIR}/{out_dir}")
    output_path.mkdir(exist_ok=True)

    all_claims: list[dict[str, Any]] = []

    for row in df.toLocalIterator():
        file_path = row["filename"]
        content = row["content"]
        file_name = (
            Path(file_path).name.replace(".txt", ".json").replace(".dat", ".json")
        )

        logger.info(f"📄 Parsing file: {file_name}")

        try:
            edi = EDI(content, strict_transactions=False)
            claims = hm.from_edi(edi)

            parsed_claims = []
            for c in claims:
                claim_dict = c.to_json() if hasattr(c, "to_json") else c
                if isinstance(claim_dict, dict):
                    claim_dict["source_file"] = file_name
                    parsed_claims.append(claim_dict)
                    all_claims.append(claim_dict)

            with open(output_path / file_name, "w") as f:
                json.dump(parsed_claims, f, indent=2)

            logger.info(f"✅ Saved: {file_name}")

        except Exception as e:
            logger.error(f"❌ Error parsing {file_name}: {e}")

    return all_claims


def parse_edi_files_glob(glob_path: str, repartition: int = 4) -> list[dict[str, Any]]:
    """
    Parse all EDI 837 files matching the glob path and return structured claims as JSON dicts.
    """
    spark = SparkSession.builder.appName("EDI837Parser").getOrCreate()
    hm = HealthcareManager()

    # Read all EDI files as whole text
    df = spark.read.text(glob_path, wholetext=True)
    df = df.withColumn("filename", input_file_name())

    # Parse and flatten claims
    rdd = (
        df.rdd.map(lambda row: (row.filename, EDI(row.value)))
        .map(lambda edi: hm.flatten(edi[1], filename=edi[0]))
        .flatMap(lambda x: x)
    )

    # Optional repartition for parallelism
    rdd = rdd.repartition(repartition)

    # Convert to JSON strings
    claims_rdd = rdd.map(lambda x: hm.flatten_to_json(x)).map(json.dumps)

    # Load as structured DataFrame
    claims_df = spark.read.json(claims_rdd)

    logger.info(f"📄 Parsed {claims_df.count()} claims from: {glob_path}")
    return claims_df.collect()
