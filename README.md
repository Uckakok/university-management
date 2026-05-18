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

Layer

Technology

Backend

FastAPI, Python, MySQL Connector

Frontend

HTML, CSS, JavaScript, Fetch API

Database

MySQL 8.0

Authentication

JWT (python-jose)

Environment Management

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

Method

Endpoint

Description

POST

`/register`

Create a new account

POST

`/login`

Authenticate user

GET

`/metadata/genders`

Retrieve gender options

### Student

Method

Endpoint

Description

GET

`/get_dashboard_data`

Get profile/dashboard data

POST

`/register_candidate`

Submit candidate information

GET

`/get_available_programmes`

View available programmes

POST

`/submit_application`

Submit programme application

GET

`/view_applications`

View submitted applications

GET

`/get_current_courses`

View enrolled courses and grades

GET

`/get_eligible_courses`

View available courses

POST

`/register_for_course`

Register for a course

### Admin

Method

Endpoint

Description

GET

`/get_applications`

View pending applications

POST

`/approve_application`

Approve application

POST

`/reject_application`

Reject application

POST

`/issue_grade`

Assign grades

POST

`/complete_course`

Mark course as completed

POST

`/process_semester_transition`

Process semester advancement

GET

`/get_registrations`

View all registrations

Installation & Setup
--------------------

### Prerequisites

*   Python 3.x
    
*   MySQL 8.0
    

### Backend Setup

1.  Install dependencies:
    

Bash

    pip install -r requirements.txt

2.  Configure environment variables:
    

Bash

    cp .env.example .env

3.  Update `.env` with your database credentials.
    
4.  Run deployment script:
    

Bash

    python deploy.py

5.  Start the backend server:
    

Bash

    python -m uvicorn main:app --reload

### Frontend Setup

Open the frontend files from the `Frontend/` directory in your browser or run them using a local development server (recommended: Live Server on port 5500).

Database Users
--------------

User

Permissions

`app_guest`

Registration and login only

`app_student`

Student operations through stored procedures

`app_admin`

Administrative operations

Project Status
--------------

> This project is a development version intended for educational and demonstration purposes.
