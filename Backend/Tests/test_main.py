from fastapi.testclient import TestClient
from faker import Faker
import sys
import os
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

fake = Faker()
client = TestClient(app)


def test_register_success():
    response = client.post(
        "/register",
        json={
            "name": "Test",
            "surname": "User",
            "login": "testuser_unique_1",
            "password": "securepassword",
            "gender": "Male",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_register_duplicate_login():
    payload = {
        "name": "Duplicate",
        "surname": "User",
        "login": "testuser_unique_1",
        "password": "password",
        "gender": "Male",
    }
    client.post("/register", json=payload)
    response = client.post("/register", json=payload)
    assert response.status_code == 400
    assert "Duplicate entry" in response.json()["detail"]


def test_register_invalid_data():
    payload = {
        "name": "Du",
        "surname": "unique_user_1",
        "login": "testuser_unique_2",
        "password": "password",
        "gender": "Male",
    }
    client.post("/register", json=payload)
    response = client.post("/register", json=payload)
    assert response.status_code == 422
    assert any("String should" in error["msg"] for error in response.json()["detail"])


def test_login_success():
    register_payload = {
        "name": "Test",
        "surname": "User",
        "login": "testuser_unique_1",
        "password": "securepassword",
        "gender": "Male",
    }
    client.post("/register", json=register_payload)

    response = client.post(
        "/login", data={"username": "testuser_unique_1", "password": "securepassword"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password():
    register_payload = {
        "name": "Test",
        "surname": "User",
        "login": "testuser_unique_2",
        "password": "securepassword",
        "gender": "Male",
    }
    client.post("/register", json=register_payload)

    response = client.post(
        "/login", data={"username": "testuser_unique_2", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid login or password"


def test_login_nonexistent_user():
    response = client.post(
        "/login",
        data={"username": "user_that_does_not_exist", "password": "anypassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid login or password"


def get_auth_token():
    login = fake.user_name() + "_" + fake.numerify(text="%%%")
    password = "securepassword123"

    register_payload = {
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "login": login,
        "password": password,
        "gender": fake.random_element(elements=("Male", "Female")),
    }

    client.post("/register", json=register_payload)

    response = client.post("/login", data={"username": login, "password": password})

    return {
        "token": response.json()["access_token"],
        "login": login,
        "password": password,
    }


def test_register_candidate_success():
    auth_data = get_auth_token()

    response = client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": fake.numerify(text="###########"),
            "email_address": fake.email(),
            "phone_number": "123123123",
            "address": fake.address(),
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_register_candidate_invalid_data():
    auth_data = get_auth_token()

    response = client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": "123",
            "email_address": fake.email(),
            "phone_number": "123123123",
            "address": fake.address(),
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )
    assert response.status_code == 422


def test_register_candidate_unauthorized():
    response = client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": "12345678901",
            "email_address": "candidate@example.com",
            "phone_number": "+48123456789",
            "address": "123 Main Street",
        },
    )
    assert response.status_code == 401


def test_get_dashboard_data_success():
    auth_data = get_auth_token()

    response = client.get(
        "/get_dashboard_data", headers={"Authorization": f"Bearer {auth_data['token']}"}
    )

    assert response.status_code == 200
    assert "has_profile" in response.json()
    assert "login" in response.json()
    assert response.json()["login"] == auth_data["login"]
    assert response.json()["has_profile"] in [0, 1] 


def test_get_dashboard_data_with_profile():
    auth_data = get_auth_token()

    client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": fake.numerify(text="###########"),
            "email_address": fake.email(),
            "phone_number": "123123123",
            "address": fake.address(),
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )

    response = client.get(
        "/get_dashboard_data", headers={"Authorization": f"Bearer {auth_data['token']}"}
    )

    assert response.status_code == 200
    assert response.json()["has_profile"] == 1
    assert response.json()["login"] == auth_data["login"]


def test_get_dashboard_data_unauthorized():
    response = client.get("/get_dashboard_data")
    assert response.status_code == 401

def test_get_available_programmes_success():
    """Test getting available programmes (no auth required)"""
    response = client.get("/get_available_programmes")
    
    assert response.status_code == 200
    assert "programmes" in response.json()
    assert isinstance(response.json()["programmes"], list)


def test_submit_application_success():
    """Test submitting an application"""
    auth_data = get_auth_token()
    
    # First register as candidate
    client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": fake.numerify(text="###########"),
            "email_address": fake.email(),
            "phone_number": "123123123",
            "address": fake.address(),
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )
    
    # Get available programmes first
    programmes_response = client.get("/get_available_programmes")
    assert programmes_response.status_code == 200
    programmes = programmes_response.json()["programmes"]
    
    if len(programmes) > 0:
        response = client.post(
            "/submit_application",
            json={
                "id_programme": programmes[0]["id_programme"],
                "motivation_letter": "I am very motivated to join this programme"
            },
            headers={"Authorization": f"Bearer {auth_data['token']}"},
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"


def test_submit_application_unauthorized():
    """Test submitting application without authentication"""
    response = client.post(
        "/submit_application",
        json={
            "id_programme": 1,
            "motivation_letter": "Test motivation letter"
        },
    )
    assert response.status_code == 401


def test_view_applications_success():
    """Test viewing user's own applications"""
    auth_data = get_auth_token()
    
    response = client.get(
        "/view_applications",
        headers={"Authorization": f"Bearer {auth_data['token']}"}
    )
    
    assert response.status_code == 200
    assert "applications" in response.json()
    assert isinstance(response.json()["applications"], list)


def test_view_applications_unauthorized():
    """Test viewing applications without authentication"""
    response = client.get("/view_applications")
    assert response.status_code == 401


def test_get_eligible_courses_success():
    """Test getting eligible courses for a student"""
    auth_data = get_auth_token()
    
    # First register as candidate
    client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": fake.numerify(text="###########"),
            "email_address": fake.email(),
            "phone_number": "123123123",
            "address": fake.address(),
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )

    programmes_response = client.get("/get_available_programmes")
    assert programmes_response.status_code == 200
    programmes = programmes_response.json()["programmes"]
    
    assert len(programmes) > 0

    response = client.post(
        "/submit_application",
        json={
            "id_programme": programmes[0]["id_programme"],
            "motivation_letter": "I am very motivated to join this programme"
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )

    admin_auth = get_admin_auth_token()
    
    response = client.post(
        "/approve_application",
        json={"id_application": 1},
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200

    response = client.get(
        "/get_eligible_courses",
        headers={"Authorization": f"Bearer {auth_data['token']}"}
    )

    assert response.status_code == 200
    assert "eligible_courses" in response.json()
    assert isinstance(response.json()["eligible_courses"], list)


def test_get_eligible_courses_unauthorized():
    """Test getting eligible courses without authentication"""
    response = client.get("/get_eligible_courses")
    assert response.status_code == 401


def test_get_current_courses_success():
    auth_data = get_auth_token()
    
    # First register as candidate
    client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": fake.numerify(text="###########"),
            "email_address": fake.email(),
            "phone_number": "123123123",
            "address": fake.address(),
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )

    programmes_response = client.get("/get_available_programmes")
    assert programmes_response.status_code == 200
    programmes = programmes_response.json()["programmes"]
    
    assert len(programmes) > 0

    response = client.post(
        "/submit_application",
        json={
            "id_programme": programmes[0]["id_programme"],
            "motivation_letter": "I am very motivated to join this programme"
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )

    admin_auth = get_admin_auth_token()
    
    response = client.post(
        "/approve_application",
        json={"id_application": 1},
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200
    
    response = client.get(
        "/get_current_courses",
        headers={"Authorization": f"Bearer {auth_data['token']}"}
    )
    
    assert response.status_code == 200
    assert "current_courses" in response.json()
    assert isinstance(response.json()["current_courses"], list)


def test_get_current_courses_unauthorized():
    """Test getting current courses without authentication"""
    response = client.get("/get_current_courses")
    assert response.status_code == 401


def test_register_for_course_success():
    """Test registering for a course"""
    auth_data = get_auth_token()
    
    # First register as candidate
    client.post(
        "/register_candidate",
        json={
            "nationality": "PL",
            "pesel": fake.numerify(text="###########"),
            "email_address": fake.email(),
            "phone_number": "123123123",
            "address": fake.address(),
        },
        headers={"Authorization": f"Bearer {auth_data['token']}"},
    )
    
    # Get eligible courses
    eligible_response = client.get(
        "/get_eligible_courses",
        headers={"Authorization": f"Bearer {auth_data['token']}"}
    )
    
    if eligible_response.status_code == 200:
        courses = eligible_response.json().get("eligible_courses", [])
        if len(courses) > 0:
            response = client.post(
                "/register_for_course",
                json={"course_id": courses[0]["id_course_in_cycle"]},
                headers={"Authorization": f"Bearer {auth_data['token']}"}
            )
            
            assert response.status_code == 200
            assert response.json()["status"] == "success"


def test_register_for_course_unauthorized():
    """Test registering for course without authentication"""
    response = client.post(
        "/register_for_course",
        json={"course_id": 1}
    )
    assert response.status_code == 401


def get_admin_auth_token():
    password = 'password'
    hashed_password = hashlib.sha256(password.encode()).hexdigest().lower()

    response = client.post("/login", data={"username": 'login', "password": hashed_password})

    
    assert response.status_code == 200
    return {
        "token": response.json()["access_token"],
        "login": 'login',
        "password": hashed_password,
    }


def test_get_applications_admin():
    """Test getting all applications (admin only)"""
    admin_auth = get_admin_auth_token()
    
    response = client.get(
        "/get_applications",
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200
    assert "applications" in response.json()
    assert isinstance(response.json()["applications"], list)


def test_get_applications_unauthorized():
    """Test getting applications without admin role"""
    auth_data = get_auth_token()
    
    response = client.get(
        "/get_applications",
        headers={"Authorization": f"Bearer {auth_data['token']}"}
    )
    
    assert response.status_code == 403 or response.status_code == 401


def test_get_registrations_admin():
    """Test getting all registrations (admin only)"""
    admin_auth = get_admin_auth_token()
    
    response = client.get(
        "/get_registrations",
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200
    assert "registrations" in response.json()
    assert isinstance(response.json()["registrations"], list)


def test_get_registrations_unauthorized():
    """Test getting registrations without admin role"""
    auth_data = get_auth_token()
    
    response = client.get(
        "/get_registrations",
        headers={"Authorization": f"Bearer {auth_data['token']}"}
    )
    
    assert response.status_code == 403 or response.status_code == 401


def test_approve_application_admin():
    """Test approving an application (admin only)"""
    admin_auth = get_admin_auth_token()
    
    # First create a test application
    # This would require a full flow: register candidate -> submit application
    # Then approve it
    response = client.post(
        "/approve_application",
        json={"id_application": 1},  # Use a valid application ID
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    # Since we don't know if ID 1 exists, either 200 or 400 is acceptable
    assert response.status_code == 200


def test_reject_application_admin():
    """Test rejecting an application (admin only)"""
    admin_auth = get_admin_auth_token()
    
    response = client.post(
        "/reject_application",
        json={"id_application": 1},  # Use a valid application ID
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200


def test_process_semester_transition_admin():
    """Test processing semester transition (admin only)"""
    admin_auth = get_admin_auth_token()
    
    response = client.post(
        "/process_semester_transition",
        json={"id_student": 1},  # Use a valid student ID
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200


def test_complete_course_admin():
    """Test completing a course (admin only)"""
    admin_auth = get_admin_auth_token()
    
    response = client.post(
        "/complete_course",
        json={
            "id_student": 1,  # Use valid IDs
            "id_course_in_cycle": 1
        },
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200


def test_issue_grade_admin():
    """Test issuing a grade (admin only)"""
    admin_auth = get_admin_auth_token()
    
    response = client.post(
        "/issue_grade",
        json={
            "id_registration": 1,  # Use a valid registration ID
            "grade_value": "5.0",
            "comment": "Excellent work"
        },
        headers={"Authorization": f"Bearer {admin_auth['token']}"}
    )
    
    assert response.status_code == 200