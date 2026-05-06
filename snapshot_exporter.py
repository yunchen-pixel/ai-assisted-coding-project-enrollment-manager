from __future__ import annotations

import json
from pathlib import Path

from config import CURRENT_STUDENT, SNAPSHOT_PATH
from enrollment_database import EnrollmentDatabase

def export_database_snapshot(
    database: EnrollmentDatabase,
    path: Path = SNAPSHOT_PATH,
) -> None:
    snapshot = {
        "current_student": CURRENT_STUDENT,
        "available_course_keys": database.get_available_course_keys(),
        "enrollment_table": database.get_all_enrollment_records(),
    }
    path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
