# tests/worker_kafka/edi_etl/test_edi_transform.py

from datetime import datetime, date, time
from care_gateway.worker_kafka.edi_etl.edi_transform import (
    map_date_code_to_event_type,
    normalize_field_name,
    normalize_date_format,
    parse_date,
    safe_float,
    extract_claim_events_from_dates,
    convert_to_claim_with_events,
)


def test_map_date_code_to_event_type_known():
    assert map_date_code_to_event_type("434") == "Service Period"


def test_map_date_code_to_event_type_unknown():
    assert map_date_code_to_event_type("999") == "Unknown Code 999"


def test_normalize_field_name():
    assert normalize_field_name("patient_name") == "Patient Name"


def test_normalize_date_format_known():
    assert normalize_date_format("D8") == "YYYYMMDD"


def test_normalize_date_format_unknown():
    assert normalize_date_format("XYZ") == "XYZ"


def test_parse_date_valid():
    assert parse_date("20240506") == date(2024, 5, 6)


def test_parse_date_invalid():
    assert parse_date("badinput") is None


def test_safe_float_valid():
    assert safe_float("123.45") == 123.45


def test_safe_float_invalid():
    assert safe_float("notanumber") is None


def test_extract_claim_events_from_dates_d8():
    events = extract_claim_events_from_dates(
        1, [{"date_cd": "431", "date_format": "D8", "date": "20240506"}]
    )
    assert len(events) == 1
    assert events[0].event_date == date(2024, 5, 6)


def test_extract_claim_events_from_dates_tm():
    events = extract_claim_events_from_dates(
        1, [{"date_cd": "431", "date_format": "TM", "date": "1230"}]
    )
    assert len(events) == 1
    assert events[0].event_time.time() == time(12, 30)


def test_convert_to_claim_with_events():
    record = {
        "patient": {"name": "john doe", "dob": "19900101"},
        "claim_header": {
            "claim_id": "CL123",
            "claim_amount": "100.50",
            "claim_dates": [
                {"date_cd": "431", "date_format": "D8", "date": "20240506"}
            ],
        },
        "source_file": "source.txt",
    }

    claim, events = convert_to_claim_with_events(record)
    assert claim.reference_id == "CL123"
    assert claim.patient_name == "John Doe"
    assert claim.claim_amount == 100.50
    assert len(events) == 1


def test_extract_claim_events_with_datetime_format():
    events = extract_claim_events_from_dates(
        1, [{"date_cd": "435", "date_format": "DT", "date": "20240506123000"}]
    )
    assert len(events) == 1
    assert events[0].event_datetime == datetime(2024, 5, 6, 12, 30)


def test_extract_claim_events_with_invalid_tm_format_graceful():
    events = extract_claim_events_from_dates(
        1, [{"date_cd": "090", "date_format": "TM", "date": "9999"}]
    )
    assert len(events) == 0


def test_extract_claim_events_with_rd8_format():
    events = extract_claim_events_from_dates(
        1, [{"date_cd": "431", "date_format": "RD8", "date": "20240501-20240506"}]
    )
    assert len(events) == 1
    assert events[0].event_date == date(2024, 5, 1)


def test_parse_date_none_on_short_input():
    assert parse_date("2024") is None
