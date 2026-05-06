# Enrollment Structure Analysis

| Structural Issue | Example From My Code | Why It Is a Problem | Suggested Future Layer |
|---|---|---|---|
| Constants and configuration are mixed into the main backend file | DB_PATH, SNAPSHOT_PATH, CURRENT_STUDENT, statuses, and course key lists are all stored near the top of the same file | This makes the file harder to manage as the project grows. If paths, statuses, or sample data change, they are mixed with the actual backend logic | Constants/Config |
| Database setup and database queries are mixed with other responsibilities | connect, create_tables, seed_sample_data, get_available_course_keys, get_course_by_key, and get_student_enrollments all directly use SQLite | These functions belong together, but they should be separated from service logic so the database layer has one clear responsibility | Database Class |
| Some functions combine business rules and database updates | enroll_with_key checks user_id, email, enrollment_key, finds the course, inserts or updates enrollment status, and returns a record | This is a cross-layer problem because one function is doing validation, enrollment decision-making, and database writing. This can make the function harder to test and change later | Needs Splitting |
| Soft unenrollment mixes service meaning with database update | soft_unenroll_student changes the status to unenrolled instead of deleting the record | The database update is simple, but the decision to keep history by using status is a service-level rule. This should be clearer in a service layer | Needs Splitting |
| Summary logic depends on enrollment history | get_student_summary calls get_student_enrollment_history and counts enrolled and unenrolled records | This is service-level behavior because it explains what the data means instead of just reading rows from the database | Service Class |
| JSON export combines reading database data and writing an output file | export_database_snapshot collects current student, course keys, and enrollment records, then writes a JSON file | This mixes data access with export/reporting responsibility. If the export format changes, it could affect backend database logic | Needs Splitting |
| The main runner is mixed with backend behavior | main creates tables, seeds data, prints student information, enrolls a student, shows summary, and exports a snapshot | This is useful for testing, but it should not stay mixed with the main backend logic. It should become a separate runner or test flow | Needs Splitting |
| SQL statements are spread across many functions | SELECT, INSERT, UPDATE, JOIN, and table creation SQL are written directly inside multiple functions | This can make future changes harder because database details are scattered. A database class would make the backend easier to maintain | Database Class |

## Most Important Findings

The current backend works, but it is too procedural and mixed together. The biggest issue is that some functions are doing more than one kind of work. For example, enroll_with_key is not only updating the database. It also checks inputs, finds the course, applies the enrollment rule, and decides how to reactivate a student. This should be split later so a service class handles the enrollment logic and a database class handles the SQL work.

The cleanest future design would separate the project into constants/config, a database class, a service class, and a small runner or test file. The database class should focus on SQLite connections, tables, queries, inserts, and updates. The service class should focus on enrollment rules, summaries, and student actions. Constants such as paths, statuses, and sample course keys should be moved out of the main logic.

# Backend Refactor Plan

## Goal

The goal is to change the backend from one procedural file into a clearer layered design. The database layer should handle SQLite work. The service layer should handle student enrollment meaning and rules. The runner should only be used to test the backend flow.

## Suggested File and Class Structure

| File or Class | Main Responsibility |
|---|---|
| config.py | Store constants such as DB_PATH, SNAPSHOT_PATH, statuses, current student, and sample course data |
| enrollment_database.py / EnrollmentDatabase | Handle SQLite connection, table creation, seed data, SELECT queries, INSERT, and UPDATE statements |
| enrollment_service.py / EnrollmentService | Handle enrollment-key logic, student enrollment actions, soft unenrollment rules, and summary counting |
| snapshot_exporter.py | Export database information into a JSON snapshot |
| practice_runner.py | Run the backend in the terminal for testing before the UI exists |

## What Should Move to the Database Class

The database class should include the functions that mainly work with SQLite rows and SQL statements. This includes connect, create_tables, seed_sample_data, get_available_course_keys, get_course_by_key, get_student_enrollments, get_student_enrollment_history, get_student_course_record, get_all_enrollment_records, and the SQL SELECT, INSERT, and UPDATE logic.

## What Should Move to the Service Class

The service class should include functions that explain what student actions mean. enroll_with_key should become service-level logic because it validates the student information, checks the enrollment key, decides whether the course exists, and asks the database layer to insert or reactivate the enrollment. soft_unenroll_student should also be service-level because the decision to keep the record and mark it as unenrolled is a business rule. get_student_summary should stay in the service layer because it counts and explains the student's enrollment status.

## What Should Stay Separate

Constants and sample data should be separated from the main backend logic. The JSON snapshot export should also be separated because it is more like a reporting/export task. The main runner should not be mixed with the backend classes because it is only used to test behavior.

## Safe Implementation Order

1. Create a config file for constants and sample data.
2. Create an EnrollmentDatabase class and move database connection, table creation, seed data, and query functions into it.
3. Create an EnrollmentService class that receives an EnrollmentDatabase object.
4. Move enroll_with_key, soft_unenroll_student, and get_student_summary into the service class.
5. Create a snapshot exporter function that uses the service/database layer to collect data and write JSON.
6. Update the main runner so it imports the new classes and tests the same behavior as before.
7. Run the project and make sure the printed output and JSON snapshot still work.

## Implementation Prompt To Use Later

Please refactor my student enrollment backend into a simple layered object-oriented design. Create a config/constants section or file, an EnrollmentDatabase class for SQLite connection, table creation, seed data, SELECT queries, INSERT, and UPDATE logic, and an EnrollmentService class for enrollment-key validation, student enrollment actions, soft unenrollment, and summary counting. Keep the JSON snapshot export separate from the service and database classes. Keep the terminal runner separate from the backend classes. Do not add UI features. Make sure the behavior stays the same as the original starter code.