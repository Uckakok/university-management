start transaction;

insert into
    people (
        name,
        second_name,
        surname,
        gender
    )
values ('John', NULL, 'Smith', 'Male'),
    (
        'Anna',
        NULL,
        'Kowalska',
        'Female'
    ),
    (
        'Robert',
        NULL,
        'Nowak',
        'Male'
    ),
    (
        'Emily',
        NULL,
        'Johnson',
        'Female'
    ),
    (
        'Michael',
        NULL,
        'Brown',
        'Male'
    );

insert into
    contact_info (
        id_people,
        email_address,
        phone_number,
        address
    )
values (
        1,
        'john.smith@uni.edu',
        '+48111111111',
        'Warsaw'
    ),
    (
        2,
        'anna.kowalska@uni.edu',
        '+48222222222',
        'Krakow'
    ),
    (
        3,
        'robert.nowak@uni.edu',
        '+48333333333',
        'Gdansk'
    ),
    (
        4,
        'emily.johnson@uni.edu',
        '+48444444444',
        'Poznan'
    ),
    (
        5,
        'michael.brown@uni.edu',
        '+48555555555',
        'Wroclaw'
    );

insert into
    employees (
        id_people,
        academic_title,
        employment_start
    )
values (1, 'Professor', NOW()),
    (2, 'PhD', NOW()),
    (3, 'Professor', NOW()),
    (4, 'PhD', NOW()),
    (5, 'MSc', NOW());

insert into
    system_user(
        id_people,
        system_role,
        login,
        password_hash
    )
values (
        1,
        'professor',
        'jsmith',
        SHA2('admin123', 256)
    ),
    (
        2,
        'professor',
        'akowalska',
        SHA2('admin123', 256)
    ),
    (
        3,
        'administrator',
        'rnowak',
        SHA2('admin123', 256)
    ),
    (
        4,
        'professor',
        'ejohnson',
        SHA2('admin123', 256)
    ),
    (
        5,
        'professor',
        'mbrown',
        SHA2('admin123', 256)
    );

insert into
    departments (
        name,
        abbreviation,
        address,
        phone_number,
        email_address,
        id_dean
    )
values (
        'Department of Computer Science',
        'CS',
        'Warsaw Campus',
        '+48100100100',
        'cs@uni.edu',
        1
    ),
    (
        'Department of Mathematics',
        'MATH',
        'Krakow Campus',
        '+48200200200',
        'math@uni.edu',
        3
    ),
    (
        'Department of Physics',
        'PHYS',
        'Gdansk Campus',
        '+48300300300',
        'physics@uni.edu',
        4
    );

insert into
    programmes (
        name,
        degree,
        form_of_study,
        id_department,
        language
    )
values (
        'Computer Science',
        1,
        'full-time',
        1,
        'en'
    ),
    (
        'Applied Mathematics',
        1,
        'full-time',
        2,
        'en'
    ),
    (
        'Physics',
        1,
        'full-time',
        3,
        'en'
    );

insert into
    semesters (
        name,
        start_time,
        end_time,
        academic_year,
        semester_number
    )
values (
        'Winter 2025',
        '2025-10-01',
        '2026-02-15',
        '2025/2026',
        1
    ),
    (
        'Summer 2026',
        '2026-02-20',
        '2026-06-30',
        '2025/2026',
        2
    );

insert into
    courses (
        name,
        course_code,
        ects_credits,
        lecture_hours,
        practical_classes_hours,
        laboratory_hours,
        form_of_assesment,
        mode
    )
values (
        'Programming 101',
        'CS101',
        6,
        30,
        15,
        30,
        'exam',
        1
    ),
    (
        'Databases',
        'CS102',
        5,
        30,
        15,
        15,
        'exam',
        1
    ),
    (
        'Calculus I',
        'MATH101',
        6,
        45,
        30,
        0,
        'exam',
        1
    ),
    (
        'Linear Algebra',
        'MATH102',
        5,
        30,
        30,
        0,
        'exam',
        1
    ),
    (
        'Classical Mechanics',
        'PHYS101',
        6,
        45,
        15,
        15,
        'exam',
        1
    ),
    (
        'Electromagnetism',
        'PHYS102',
        5,
        30,
        15,
        15,
        'exam',
        1
    );

insert into
    programme_courses (
        id_course,
        id_programme,
        semester_number,
        is_mandatory
    )
values (1, 1, 1, TRUE),
    (2, 1, 2, TRUE),
    (3, 2, 1, TRUE),
    (4, 2, 2, TRUE),
    (5, 3, 1, TRUE),
    (6, 3, 2, TRUE);

insert into
    courses_in_cycles (
        id_course,
        id_semester,
        participants_limit,
        id_coordinator,
        syllabus
    )
values (
        1,
        1,
        120,
        1,
        'Introductory programming'
    ),
    (
        2,
        2,
        100,
        2,
        'Database systems'
    ),
    (
        3,
        1,
        80,
        3,
        'Differential calculus'
    ),
    (4, 2, 80, 3, 'Linear algebra'),
    (
        5,
        1,
        60,
        4,
        'Newtonian mechanics'
    ),
    (
        6,
        2,
        60,
        4,
        'Electromagnetic theory'
    );

insert into
    course_groupes (
        id_course_in_cycle,
        id_groupe_type,
        participants_limit,
        is_active
    )
values (1, 1, 120, TRUE),
    (1, 2, 30, TRUE),
    (1, 3, 20, TRUE),
    (2, 1, 100, TRUE),
    (2, 3, 20, TRUE),
    (3, 1, 80, TRUE),
    (3, 2, 30, TRUE),
    (4, 1, 80, TRUE),
    (5, 1, 60, TRUE),
    (5, 3, 20, TRUE),
    (6, 1, 60, TRUE);

insert into
    instructor_assignment (id_course_groupe, id_employee)
values (1, 1),
    (2, 2),
    (3, 5),
    (4, 2),
    (5, 5),
    (6, 3),
    (7, 3),
    (8, 3),
    (9, 4),
    (10, 4),
    (11, 4);

insert into
    programme_requirements (
        id_programme,
        semester_number,
        min_ects_to_pass_semester,
        min_ects_to_graduate,
        mandatory_courses_passed_required
    )
values (1, 1, 30, 180, TRUE),
    (1, 2, 30, 180, TRUE),
    (2, 1, 30, 180, TRUE),
    (2, 2, 30, 180, TRUE),
    (3, 1, 30, 180, TRUE),
    (3, 2, 30, 180, TRUE);

commit;