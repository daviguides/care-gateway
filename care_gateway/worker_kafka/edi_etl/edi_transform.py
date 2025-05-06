from datetime import date, datetime
from typing import Any

from care_gateway.db.sqlmodel_models.models import Claim, ClaimEvent

DATE_CODE_MAPPING: dict[str, str] = {
    "434": "Service Period",
    "435": "Admission DateTime",
    "096": "Discharge Time",
    "050": "Service Approval",
    "454": "End Date",
    "573": "Claim Creation",
    "304": "End of Period",
    "314": "Service Range",
    "439": "Date of Incident",
    "444": "Release Date",
    "453": "Start of Care",
    "455": "Certification Date",
    "484": "Begin Therapy",
    "090": "Initial Contact",
    "091": "Follow-up",
    "431": "Occurrence Date",
}


def map_date_code_to_event_type(code: str) -> str:
    return DATE_CODE_MAPPING.get(code.strip(), f"Unknown Code {code}")


def normalize_field_name(name: str) -> str:
    parts = name.strip().replace("_", " ").split()
    return " ".join(part.capitalize() for part in parts)


def normalize_date_format(raw_format: str) -> str:
    return {
        "D8": "YYYYMMDD",
        "RD8": "YYYYMMDD-YYYYMMDD",
        "DT": "DateTime",
        "TM": "Time",
    }.get(raw_format.strip(), raw_format)


def extract_claim_events_from_dates(
    claim_id: int,
    claim_dates: list[dict[str, Any]],
) -> list[ClaimEvent]:
    events: list[ClaimEvent] = []

    for item in claim_dates:
        code: str | None = item.get("date_cd")
        fmt: str | None = item.get("date_format")
        raw_date: str | None = item.get("date")

        event_type: str = map_date_code_to_event_type(code or "")
        event = ClaimEvent(
            claim_id=claim_id,
            event_type=event_type,
            raw_code=code,
            raw_format=fmt,
        )

        try:
            if fmt == "D8" and raw_date and len(raw_date) == 8:
                event.event_date = datetime.strptime(raw_date, "%Y%m%d").date()
            elif fmt == "DT" and raw_date and len(raw_date) >= 12:
                event.event_datetime = datetime.strptime(raw_date[:12], "%Y%m%d%H%M")
            elif fmt == "TM" and raw_date and len(raw_date) >= 4:
                parsed_time = datetime.strptime(raw_date[:4], "%H%M").time()
                event.event_time = datetime.combine(date.today(), parsed_time)
            elif fmt == "RD8" and raw_date and "-" in raw_date:
                start_date, *_ = raw_date.split("-")
                event.event_date = datetime.strptime(start_date, "%Y%m%d").date()
        except Exception:
            continue

        events.append(event)

    return events


def parse_date(raw: str | None) -> date | None:
    if raw and len(raw) >= 8:
        try:
            return datetime.strptime(raw[:8], "%Y%m%d").date()
        except ValueError:
            return None
    return None


def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def convert_to_claim_with_events(
    record: dict[str, Any],
) -> tuple[Claim, list[ClaimEvent]]:
    patient = record.get("patient", {})
    header = record.get("claim_header", {})

    reference_id = header.get("claim_id") or record.get("source_file")
    patient_name = normalize_field_name(patient.get("name"))
    patient_dob = parse_date(patient.get("dob"))
    claim_amount = safe_float(header.get("claim_amount"))
    imported_from = record.get("source_file")
    claim_date = parse_date(
        next(
            (
                d["date"]
                for d in header.get("claim_dates", [])
                if d.get("date_cd") == "431"
            ),
            None,
        )
    )

    claim = Claim(
        reference_id=reference_id,
        patient_name=patient_name,
        patient_dob=patient_dob,
        claim_amount=claim_amount,
        claim_date=claim_date,
        imported_from=imported_from,
    )

    events = extract_claim_events_from_dates(
        claim_id=0,  # temporário, será preenchido após flush
        claim_dates=header.get("claim_dates", []),
    )

    return claim, events
