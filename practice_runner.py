from __future__ import annotations

from config import CURRENT_STUDENT, SNAPSHOT_PATH
from enrollment_database import EnrollmentDatabase
from enrollment_service import EnrollmentService
from snapshot_exporter import export_database_snapshot


def main() -> None:
    database = EnrollmentDatabase()
    service = EnrollmentService(database)

    database.create_tables()
    database.seed_sample_data()

    user_id = CURRENT_STUDENT["user_id"]
    email = CURRENT_STUDENT["email"]

    print("Current student:")
    print(CURRENT_STUDENT)

    print("\nAvailable enrollment keys:")
    print(service.get_available_course_keys())

    print("\nInitial enrolled classes:")
    print(service.get_student_enrollments(user_id))

    print("\nStudent enters key DATA210-SPRING:")
    print(service.enroll_with_key(user_id, email, "DATA210-SPRING"))

    print("\nUpdated enrolled classes:")
    print(service.get_student_enrollments(user_id))

    print("\nStudent summary:")
    print(service.get_student_summary(user_id))

    export_database_snapshot(database)
    print(f"\nDatabase snapshot written to: {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
