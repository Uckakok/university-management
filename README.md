University Management System
============================
A web-based university management platform built with **FastAPI**, **MySQL**, and **JavaScript** for handling student admissions, course enrollment, academic progression, and administrative operations.
Features
--------
### Authentication & Authorization
*   JWT-based authentication
*   Role-based access control for:
    *   Students
    *   Administrators
    *   Guests
*   Secure password hashing using SHA-256

### Student Portal
*   Account registration and login
*   Candidate profile submission
*   Browse available study programmes
*   Submit programme applications with motivation letters
*   Track application status
*   Register for semester courses
*   View enrolled courses and grades
*   Check eligible courses for future semesters

### Admin Portal
*   Review and process student applications
*   Approve or reject candidates
*   Manage student registrations
*   Assign grades
*   Mark courses as completed
*   Process semester progression
*   View all course registrations
    
Technology Stack
----------------
**Backend**
FastAPI, Python, MySQL Connector
**Frontend**
HTML, CSS, JavaScript, Fetch API
**Database**
MySQL 8.0
**Authentication**
JWT (python-jose)
**Environment Management**
python-dotenv

Database Design
---------------
The system includes relational tables for:
*   Users and authentication
*   Students and employees
*   Departments and programmes
*   Semesters and courses
*   Course groups and registrations
*   Applications and enrollments
*   Grades and course completions
*   Role assignments and graduation records

### Stored Procedures Handle
*   User registration and login
*   Student applications
*   Course registration with capacity checks
*   Grade issuance
*   Semester progression
*   Index number generation

Security
--------
*   JWT authentication with 30-minute expiration
*   Password hashing on the server side
*   Parameterized queries to prevent SQL injection
*   Role-based authorization
*   Restricted CORS configuration for development
*   Least-privilege database users:
    *   `app_guest`
    *   `app_student`
    *   `app_admin`

All database operations are performed through stored procedures to prevent direct table manipulation.

API Endpoints
-------------

### Public
`/register`
Create a new account

`/login`
Authenticate user

`/metadata/genders`
Retrieve gender options

### Student
`/get_dashboard_data`
Get profile/dashboard data

`/register_candidate`
Submit candidate information

`/get_available_programmes`
View available programmes

`/submit_application`
Submit programme application

`/view_applications`
View submitted applications

`/get_current_courses`
View enrolled courses and grades

`/get_eligible_courses`
View available courses

`/register_for_course`
Register for a course

### Admin
`/get_applications`
View pending applications

`/approve_application`
Approve application

`/reject_application`
Reject application

`/issue_grade`
Assign grades

`/complete_course`
Mark course as completed

`/process_semester_transition`
Process semester advancement

`/get_registrations`
View all registrations

Database Users
--------------

`app_guest`
Registration and login only

`app_student`
Student operations through stored procedures

`app_admin`
Administrative operations

Project Status
--------------

> This project is a development version intended for educational and demonstration purposes.
