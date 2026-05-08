from __future__ import annotations

import streamlit as st

from config import CURRENT_STUDENT
from enrollment_database import EnrollmentDatabase
from enrollment_service import EnrollmentService


def initialize_session_state() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"
    if "role" not in st.session_state:
        st.session_state.role = "student"
    if "selected_class" not in st.session_state:
        st.session_state.selected_class = None
    if "feedback_message" not in st.session_state:
        st.session_state.feedback_message = ""
    if "feedback_level" not in st.session_state:
        st.session_state.feedback_level = "info"
    if "enrollment_key" not in st.session_state:
        st.session_state.enrollment_key = ""


def set_feedback(message: str, level: str = "info") -> None:
    st.session_state.feedback_message = message
    st.session_state.feedback_level = level


def render_feedback() -> None:
    message = st.session_state.feedback_message
    level = st.session_state.feedback_level
    if not message:
        return

    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    else:
        st.info(message)


def get_selected_class_record(service: EnrollmentService) -> dict | None:
    selected_course_id = st.session_state.selected_class
    if not selected_course_id:
        return None

    enrolled = service.get_student_enrollments(CURRENT_STUDENT["user_id"])
    for record in enrolled:
        if record["course_id"] == selected_course_id:
            return record
    return None


def show_dashboard(service: EnrollmentService) -> None:
    st.title("Student Enrollment Dashboard")
    st.caption(
        f"Logged in as {CURRENT_STUDENT['name']} ({CURRENT_STUDENT['email']})"
    )

    render_feedback()

    st.subheader("Currently Enrolled Classes")
    enrolled_classes = service.get_student_enrollments(CURRENT_STUDENT["user_id"])

    if not enrolled_classes:
        st.info("You are not currently enrolled in any classes.")
    else:
        for record in enrolled_classes:
            course_id = record["course_id"]
            course_name = record["course_name"]
            instructor = record["instructor"]
            status = record["status"]

            with st.container():
                cols = st.columns([1, 3, 2, 1, 1, 1])
                cols[0].write(course_id)
                cols[1].write(f"**{course_name}**")
                cols[2].write(instructor)
                cols[3].write(status)

                if cols[4].button(
                    "Go to Class",
                    key=f"go-{course_id}",
                ):
                    st.session_state.selected_class = course_id
                    st.session_state.page = "selected_class"
                    set_feedback("", "info")

                if cols[5].button(
                    "Unenroll",
                    key=f"unenroll-{course_id}",
                ):
                    success = service.soft_unenroll_student(
                        CURRENT_STUDENT["user_id"],
                        course_id,
                    )
                    if success:
                        set_feedback(
                            f"You have been unenrolled from {course_id}.",
                            "success",
                        )
                        st.session_state.page = "dashboard"
                    else:
                        set_feedback(
                            "Unable to unenroll. Please try again.",
                            "error",
                        )

    st.markdown("---")
    st.subheader("Enroll with a Course Key")
    st.text_input(
        "Enter enrollment key",
        key="enrollment_key",
        placeholder="e.g. DATA210-SPRING",
    )
    if st.button("Enroll with Key"):
        enrollment_key = st.session_state.enrollment_key.strip()
        enrollment = service.enroll_with_key(
            CURRENT_STUDENT["user_id"],
            CURRENT_STUDENT["email"],
            enrollment_key,
        )
        if enrollment:
            set_feedback("Enrolled successfully.", "success")
            st.session_state.selected_class = enrollment["course_id"]
            st.session_state.page = "selected_class"
            st.session_state.enrollment_key = ""
        else:
            set_feedback(
                "Invalid enrollment key. Please check and try again.",
                "error",
            )


def show_selected_class_page(service: EnrollmentService) -> None:
    record = get_selected_class_record(service)

    if record is None:
        set_feedback(
            "No selected class found. Returning to the dashboard.",
            "warning",
        )
        st.session_state.page = "dashboard"
        return

    st.title("Selected Class")
    st.subheader(record["course_name"])
    st.write(f"**Course ID:** {record['course_id']}")
    st.write(f"**Instructor:** {record['instructor']}")
    st.write(f"**Enrollment status:** {record['status']}")

    st.markdown("---")
    if st.button("Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.session_state.selected_class = None
        set_feedback("", "info")


def main() -> None:
    initialize_session_state()

    if st.session_state.role != "student":
        st.error("This app is only available to student users.")
        return

    database = EnrollmentDatabase()
    service = EnrollmentService(database)

    if st.session_state.page == "selected_class":
        show_selected_class_page(service)
    else:
        show_dashboard(service)


if __name__ == "__main__":
    main()
