from __future__ import annotations

from typing import Any, Optional

from config import STATUS_ENROLLED, STATUS_UNENROLLED
from enrollment_database import EnrollmentDatabase

class EnrollmentService:
    def __init__(self, database: EnrollmentDatabase) -> None:
        self.database = database

    def enroll_with_key(
        self,
        user_id: str,
        email: str,
        enrollment_key: str,
    ) -> Optional[dict[str, Any]]:
        if not user_id or not email or "@" not in email or not enrollment_key:
            return None

        course = self.database.get_course_by_key(enrollment_key)
        if not course:
            return None

        self.database.upsert_enrollment(
            user_id,
            email,
            course["course_id"],
            STATUS_ENROLLED,
        )
        return self.database.get_student_course_record(user_id, course["course_id"])

    def soft_unenroll_student(self, user_id: str, course_id: str) -> bool:
        if not user_id or not course_id:
            return False

        return self.database.update_enrollment_status(
            user_id,
            course_id,
            STATUS_UNENROLLED,
        )

    def get_student_summary(self, user_id: str) -> dict[str, int]:
        summary = {
            "total_records": 0,
            STATUS_ENROLLED: 0,
            STATUS_UNENROLLED: 0,
        }

        for record in self.database.get_student_enrollment_history(user_id):
            summary["total_records"] += 1
            status = record["status"]
            if status in summary:
                summary[status] += 1

        return summary

    def get_available_course_keys(self) -> list[dict[str, Any]]:
        return self.database.get_available_course_keys()

    def get_student_enrollments(self, user_id: str) -> list[dict[str, Any]]:
        return self.database.get_student_enrollments(user_id)
