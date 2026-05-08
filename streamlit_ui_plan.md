# Streamlit UI Plan for Student Enrollment App

## Overview

This plan describes a simple student-facing Streamlit UI for the refactored enrollment backend. The app assumes the user is already logged in as a student and uses the seeded/current student from `config.py` as the simulated user.

The UI will use the refactored backend files:
- `config.py`
- `enrollment_database.py`
- `enrollment_service.py`
- `snapshot_exporter.py`
- `practice_runner.py`

The UI should call the `EnrollmentService` layer for enrollment actions and summary logic rather than performing direct SQL queries.

## Session State and Routing

Use `st.session_state` to track:
- `page`: current page, either `dashboard` or `selected_class`
- `role`: should be set to `student`
- `selected_class`: selected course ID or course record for navigation
- `feedback_message`: short feedback text for success/warning/error
- `feedback_level`: one of `success`, `warning`, `error`, or `info`

### Default state initialization

On app start, initialize:
- `st.session_state.page = 'dashboard'`
- `st.session_state.role = 'student'`
- `st.session_state.selected_class = None`
- `st.session_state.feedback_message = ''`
- `st.session_state.feedback_level = 'info'`

## Page 1: Student Dashboard

### Header and student info
- Use `st.title()` for app heading, e.g. "Student Enrollment Dashboard"
- Use `st.caption()` or `st.markdown()` to show current student details from `config.CURRENT_STUDENT`
- If `st.session_state.feedback_message` is set, show one of:
  - `st.success(message)` if `feedback_level == 'success'`
  - `st.warning(message)` if `feedback_level == 'warning'`
  - `st.error(message)` if `feedback_level == 'error'`
  - `st.info(message)` otherwise

### Enrolled classes display
- Use `service.get_student_enrollments(current_student['user_id'])` to load enrolled classes
- Display current enrollments with `st.dataframe()` or a custom `st.container()` list
- Each enrolled class row should include:
  - Course ID
  - Course name
  - Instructor
  - Status (should show `enrolled`)
  - Buttons: `Go to Class`, `Unenroll`

### Enrollment key form
- Use `st.text_input()` for the enrollment key input
- Use `st.button()` or `st.form_submit_button()` labeled "Enroll with Key"
- When submitted:
  - Call `service.enroll_with_key(user_id, email, enrollment_key)`
  - If the result is truthy, set `st.session_state.feedback_message = 'Enrolled successfully.'`, `feedback_level = 'success'`, and set `page = 'selected_class'` and `selected_class = course_id`
  - If the result is falsy, set `feedback_message = 'Invalid enrollment key. Please try again.'` and `feedback_level = 'error'`

### Unenroll action
- When the user clicks `Unenroll` for a class:
  - Call `service.soft_unenroll_student(user_id, course_id)`
  - If `True`, set `feedback_message = 'You have been unenrolled from {course_id}.'` and `feedback_level = 'success'`
  - If `False`, set `feedback_message = 'Unable to unenroll. Please try again.'` and `feedback_level = 'error'`
  - Refresh the dashboard view on the same page after the action

### Go to Class action
- When the user clicks `Go to Class` for a class:
  - set `st.session_state.selected_class = course_id`
  - set `st.session_state.page = 'selected_class'`
  - clear any existing `feedback_message` or keep it as needed

## Page 2: Selected Class Page

### Class detail display
- Use `selected_class` from `st.session_state`
- Load the selected record from the backend using the enrollment service or database helper
  - Example: load student history and filter the record by `course_id`
- Show basic class info with `st.write()` or `st.markdown()`:
  - Course ID
  - Course name
  - Instructor
  - Enrollment status
  - Enrolled date if available

### Navigation
- Include a button labeled `Return to Dashboard`
- When clicked, set `st.session_state.page = 'dashboard'` and keep `selected_class = None`

## Backend Calls and Integration

The Streamlit UI should use the service layer for all business actions.

### Expected service usage
- Load available enrollments: `service.get_student_enrollments(user_id)`
- Enroll with key: `service.enroll_with_key(user_id, email, enrollment_key)`
- Soft unenroll: `service.soft_unenroll_student(user_id, course_id)`
- Summary count logic can remain in the service if needed for future dashboard cards

### Backend initialization
- Create `EnrollmentDatabase()` and `EnrollmentService(database)` at app start
- Reuse those objects for UI actions
- Do not call raw SQL from the Streamlit code

## Snapshot Export Awareness

The UI plan should preserve the existing JSON snapshot export behavior from the backend and must not delete rows when unenrolling.
- The Streamlit UI should not change snapshot export design
- If desired, a small link or button can be added later to refresh/export the snapshot, but that is optional and not required in this plan

## UI Flow Summary

1. App opens on `dashboard`
2. Student sees current enrolled classes and can enter a key
3. Valid key enrolls/re-enrolls the student and navigates to the selected class page
4. Invalid key shows an error message
5. Student can `Go to Class` or `Unenroll` from the dashboard
6. `Unenroll` soft updates the enrollment status and refreshes the dashboard
7. `Go to Class` navigates to the selected class page
8. Selected class page shows class details and returns to dashboard

## Testing Checklist

- [ ] App initializes `st.session_state` keys correctly
- [ ] Default page is `dashboard`
- [ ] Current student info is displayed from `config.CURRENT_STUDENT`
- [ ] `st.session_state.role` is set to `student`
- [ ] Dashboard shows only currently enrolled classes from service layer
- [ ] Enrollment key submission calls `service.enroll_with_key()`
- [ ] Valid key produces `st.success()` and navigates to selected class page
- [ ] Invalid key produces `st.error()` and keeps the student on the dashboard
- [ ] `Go to Class` sets `page = 'selected_class'` and shows class details
- [ ] `Unenroll` calls `service.soft_unenroll_student()` and keeps the row in the database
- [ ] After unenrollment, dashboard refreshes with updated enrollments
- [ ] Navigating back from selected class returns to `dashboard`
- [ ] No authentication or registration flow is added
- [ ] Backend behavior remains unchanged from Session 1

## Notes

- Keep the UI beginner-friendly and classroom-style
- Use simple Streamlit controls: `st.title`, `st.caption`, `st.text_input`, `st.button`, `st.dataframe`, `st.container`
- Keep navigation and feedback clear through `st.session_state`
- Avoid adding any complex user-management features
