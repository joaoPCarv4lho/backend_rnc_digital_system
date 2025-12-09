from app import model

def serialize_rnc(rnc: model.RNC):
    return {
        "id": rnc.id,
        "num_rnc": rnc.num_rnc,
        "title": rnc.title,
        "status": rnc.status,
        "condition": rnc.condition,
        "part_code": rnc.part_code,
        "observations": rnc.observations,
        "critical_level": rnc.critical_level,
        "part_id": rnc.part_id,
        "open_by_id": rnc.open_by_id,
        "closed_by_id": rnc.closed_by_id,
        "date_of_occurrence": rnc.date_of_occurrence.isoformat() if rnc.date_of_occurrence else None,
        "closing_date": rnc.closing_date.isoformat() if rnc.closing_date else None,
        "close_rnc": rnc.is_closed()
    }
