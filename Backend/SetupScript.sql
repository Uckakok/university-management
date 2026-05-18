drop user if exists 'app_student'@'localhost';
drop user if exists 'app_admin'@'localhost';
drop user if exists 'app_guest'@'localhost';

create table people (
    id_people int primary key auto_increment,
    name varchar(64) not null,
    second_name varchar(64),
    surname varchar(64) not null,
    gender varchar(32) default 'not_specified'
);

create table contact_info (
    id_contact int primary key auto_increment,
    id_people int unique not null,
    email_address varchar(256),
    phone_number varchar(20),
    address varchar(256),
    foreign key (id_people) references people (id_people)
);

create table sensitive_info (
    id_sensitive int primary key auto_increment,
    id_people int not null unique,
    pesel varchar(11) unique,
    nationality varchar(2) default 'pl',
    foreign key (id_people) references people (id_people)
);

create table system_user(
    id_user int primary key auto_increment,
    id_people int not null,
    system_role enum(
        'guest',
        'student',
        'professor',
        'administrator'
    ) default 'guest',
    login varchar(32) not null unique,
    password_hash varchar(255),
    creation_date timestamp default current_timestamp,
    last_login_date timestamp null default null,
    last_login_ip binary(4),
    foreign key (id_people) references people (id_people)
);

create table roles (
    id_role int primary key auto_increment,
    name varchar(32) not null,
    description text
);

create table role_assignment (
    id_assignment int primary key auto_increment,
    id_people int not null,
    id_role int not null,
    from_datetime datetime not null default current_timestamp,
    expiration datetime default null,
    description text,
    foreign key (id_people) references people (id_people),
    foreign key (id_role) references roles (id_role)
);

create table student_status (
    id_status int primary key auto_increment,
    status_name varchar(32) unique not null
);

create table students (
    id_student int primary key auto_increment,
    id_people int not null unique,
    index_number varchar(20) unique not null,
    id_status int not null,
    enrollment_start datetime not null default current_timestamp,
    enrollment_end datetime default null,
    foreign key (id_people) references people (id_people),
    foreign key (id_status) references student_status (id_status)
);

create table employees (
    id_employee int primary key auto_increment,
    id_people int not null,
    academic_title varchar(32) not null,
    employment_start datetime default null,
    employment_end datetime default null,
    foreign key (id_people) references people (id_people)
);

create table departments (
    id_department int primary key auto_increment,
    name varchar(128) not null,
    abbreviation varchar(8) not null,
    address varchar(256),
    phone_number varchar(20),
    email_address varchar(256),
    id_dean int,
    foreign key (id_dean) references employees (id_employee)
);

create table programmes (
    id_programme int primary key auto_increment,
    name varchar(256) not null,
    degree smallint default 1,
    form_of_study varchar(64),
    id_department int not null,
    language varchar(2) not null default 'en',
    is_offered bool default true,
    foreign key (id_department) references departments (id_department)
);

create table semesters (
    id_semester int primary key auto_increment,
    name varchar(256) not null,
    start_time datetime default current_timestamp,
    end_time datetime default null,
    session_start datetime default null,
    session_end datetime default null,
    academic_year varchar(9),
    semester_number smallint
);

create table course_modes (
    id_course_mode int primary key auto_increment,
    name varchar(64) unique not null
);

create table courses (
    id_course int primary key auto_increment,
    name varchar(256) not null,
    course_code varchar(16) unique not null,
    ects_credits int default 0,
    lecture_hours int default 0,
    practical_classes_hours int default 0,
    laboratory_hours int default 0,
    project_hours int default 0,
    form_of_assesment varchar(64),
    mode int not null,
    foreign key (mode) references course_modes (id_course_mode)
);

create table courses_in_cycles (
    id_course_in_cycle int primary key auto_increment,
    id_course int not null,
    id_semester int not null,
    participants_limit int default 0,
    id_coordinator int,
    syllabus text,
    foreign key (id_course) references courses (id_course),
    foreign key (id_semester) references semesters (id_semester),
    foreign key (id_coordinator) references employees (id_employee)
);

create table programme_courses (
    id_programme_course int primary key auto_increment,
    id_course int not null,
    id_programme int not null,
    semester_number smallint not null,
    foreign key (id_course) references courses (id_course),
    foreign key (id_programme) references programmes (id_programme),
    is_mandatory boolean default true
);

create table group_types (
    id_groupe_type int primary key auto_increment,
    name varchar(64) unique not null
);

create table course_groupes (
    id_course_groupe int primary key auto_increment,
    id_course_in_cycle int not null,
    id_groupe_type int not null,
    participants_limit int default 0,
    is_active boolean,
    foreign key (id_course_in_cycle) references courses_in_cycles (id_course_in_cycle),
    foreign key (id_groupe_type) references group_types (id_groupe_type)
);

create table instructor_assignment (
    id_instructor_assignment int primary key auto_increment,
    id_course_groupe int not null,
    id_employee int not null,
    foreign key (id_course_groupe) references course_groupes (id_course_groupe),
    foreign key (id_employee) references employees (id_employee)
);

create table registrations (
    id_registration int primary key auto_increment,
    id_student int not null,
    id_course_groupe int not null,
    registration_date datetime default current_timestamp,
    foreign key (id_student) references students (id_student),
    foreign key (id_course_groupe) references course_groupes (id_course_groupe)
);

create table grades (
    id_grade int primary key auto_increment,
    id_registration int not null,
    id_employee int not null,
    grade_value varchar(8) not null,
    comment text,
    issued_at datetime default current_timestamp,
    is_corrected boolean default false,
    corrected_grade varchar(8),
    foreign key (id_registration) references registrations (id_registration),
    foreign key (id_employee) references employees (id_employee)
);

create table semester_enrollments (
    id_semester_enrollment int primary key auto_increment,
    id_student int not null,
    id_programme int not null,
    id_semester int not null,
    semester_number smallint not null,
    enrollment_date timestamp default current_timestamp,
    status enum(
        'enrolled',
        'completed',
        'failed',
        'not_enrolled'
    ) default 'not_enrolled',
    foreign key (id_student) references students (id_student),
    foreign key (id_programme) references programmes (id_programme),
    foreign key (id_semester) references semesters (id_semester)
);

create table course_completions (
    id_course_completion int primary key auto_increment,
    id_student int not null,
    id_course_in_cycle int not null,
    id_grade_final int null,
    completed_at date,
    foreign key (id_student) references students (id_student),
    foreign key (id_course_in_cycle) references courses_in_cycles (id_course_in_cycle),
    foreign key (id_grade_final) references grades (id_grade)
);

create table programme_requirements (
    id_programme_requirements int primary key auto_increment,
    id_programme int not null,
    semester_number smallint not null,
    min_ects_to_pass_semester decimal(5, 2) default 0,
    min_ects_to_graduate decimal(5, 2) default 0,
    mandatory_courses_passed_required boolean default true,
    foreign key (id_programme) references programmes (id_programme)
);

create table graduation_records (
    id_graduation_record int primary key auto_increment,
    id_student int not null,
    id_programme int not null,
    graduation_date date not null,
    diploma_number varchar(32) unique,
    final_grade_average decimal(5, 4),
    thesis_title text,
    status enum(
        'candidate',
        'approved',
        'diploma_issued'
    ) default 'candidate',
    foreign key (id_student) references students (id_student),
    foreign key (id_programme) references programmes (id_programme)
);

create table applications (
    id_application int primary key auto_increment,
    id_people int not null,
    id_programme int not null,
    status enum(
        'pending',
        'approved',
        'rejected'
    ) default 'pending',
    submitted_at datetime default current_timestamp,
    processed_at datetime default null,
    decision_by int,
    motivation_letter text,
    foreign key (id_people) references people (id_people),
    foreign key (id_programme) references programmes (id_programme),
    foreign key (decision_by) references employees (id_employee)
);

create table index_sequence (
    id_programme int not null,
    degree int not null,
    last_number int not null default 0,
    primary key (id_programme, degree)
);

insert into
    student_status (status_name)
VALUES ('active'),
    ('suspended'),
    ('graduated'),
    ('withdrawn');

insert into
    group_types (name)
VALUES ('lecture'),
    ('practical'),
    ('laboratory'),
    ('project');

insert into
    course_modes (name)
VALUES ('stationary'),
    ('online'),
    ('hybrid');

create index idx_system_user_login on system_user(login, password_hash);

create index idx_system_user_id_people on system_user(id_people);

create index idx_application_status_people on applications (status, id_people);

create index idx_applications_programme on applications (id_programme);

create index idx_semester_enrollments_student_status on semester_enrollments (id_student, status);

create index idx_semester_enrollments_programme_semester on semester_enrollments (id_programme, semester_number);

create index idx_registrations_student on registrations (id_student);

create index idx_registrations_course_group on registrations (id_course_groupe);

create index idx_course_groupes_course_cycle on course_groupes (id_course_in_cycle);

create index idx_course_completions_student_course on course_completions (
    id_student,
    id_course_in_cycle
);

create index idx_programme_courses_programme_semester on programme_courses (
    id_programme,
    semester_number,
    is_mandatory
);

create index idx_courses_in_cycles_course on courses_in_cycles (id_course);

create index idx_courses_in_cycles_semester on courses_in_cycles (id_semester);

create user 'app_student' @'localhost' identified by 'change_me';

create user 'app_admin' @'localhost' identified by 'change_me';

create user 'app_guest' @'localhost' identified by 'change_me';

delimiter //

create trigger check_course_capacity_before_insert
before insert on registrations
for each row
begin
    declare v_current_count int;
    declare v_max_limit int;
    
    select count(*), cg.participants_limit 
    into v_current_count, v_max_limit
    from course_groupes cg
    left join registrations r on r.id_course_groupe = cg.id_course_groupe
    where cg.id_course_groupe = new.id_course_groupe
    group by cg.participants_limit;
    
    if v_current_count >= v_max_limit then
        signal sqlstate '45000' 
        set message_text = 'Trigger prevented: Course group is full';
    end if;
end //

create trigger prevent_duplicate_registration
before insert on registrations
for each row
begin
	declare v_exists int;
	select count(*) into v_exists from registrations r join course_groupes cg on r.id_course_groupe = cg.id_course_groupe join courses_in_cycles cic on cg.id_course_in_cycle = cic.id_course_in_cycle where r.id_student = new.id_student and cic.id_course_in_cycle = (select id_course_in_cycle from course_groupes where id_course_groupe = new.id_course_groupe);
	if v_exists > 0 then
		signal sqlstate '45000'
		set message_text = 'Student already registered for a different group of this course';
	end if;
end //

create function employee_id_from_people_id(p_people_id int)
returns int
deterministic
reads sql data
begin
	declare v_employee_id int;
	select id_employee into v_employee_id from employees where id_people = p_people_id limit 1;
	return v_employee_id;
end //

create function student_id_from_people_id(p_people_id int)
returns int
deterministic
reads sql data
begin
	declare v_student_id int;
	select id_student into v_student_id from students where id_people = p_people_id limit 1;
	return v_student_id;
end //

create function generate_index_number (p_id_programme int)
returns varchar(20)
modifies sql data
begin
	declare v_degree int;
	declare v_counter int;
	declare v_index varchar(20);
	
	select degree into v_degree from programmes where id_programme = p_id_programme;
	if v_degree is null then
		signal sqlstate '45000' set message_text = 'Programme not found';
	end if;

	insert into index_sequence (id_programme, degree, last_number) values (p_id_programme, v_degree, 0) on duplicate key update last_number = last_number + 1;

	select last_number into v_counter from index_sequence where id_programme = p_id_programme and degree = v_degree;

	set v_index = concat(lpad(p_id_programme, 2, '0'), v_degree, lpad(v_counter, 3, '0'));
	
	while exists (select 1 from students where index_number = v_index) do
		update index_sequence set last_number = last_number + 1 where id_programme = p_id_programme and degree = v_degree;
		select last_number into v_counter from index_sequence where id_programme = p_id_programme and degree = v_degree;
		set v_index = concat(lpad(p_id_programme, 2, '0'), v_degree, lpad(v_counter, 3, '0'));
	end while;

	return v_index;
end //

create procedure register_test_admin(in p_login varchar(32), in p_password varchar(256))
begin
	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	start transaction;
	call register_user('Admin', 'Test', 'Admin', 'Not specified', p_login, p_password);

	select id_people into @admin_people_id from system_user where login = p_login;
	update system_user set system_role = 'administrator' where login = p_login;

	insert into employees (id_people, academic_title, employment_start, employment_end) values (@admin_people_id, 'Administrator', now(), null);

	commit;
end //

create procedure register_user (in p_name varchar(64), in p_second_name varchar(64), in p_surname varchar(64), in p_gender varchar(32), in p_login varchar(32), in p_password varchar(256))
begin
	declare v_hashed_password varchar(255);
	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	start transaction;
	set v_hashed_password = lower(sha2(p_password, 256));

	insert into people (name, second_name, surname, gender) values (p_name, p_second_name, p_surname, p_gender);
	set @p_id_people = last_insert_id();

	insert into system_user (id_people, system_role, login, password_hash) values (@p_id_people, 'guest', p_login, v_hashed_password);

	commit;
end //

create procedure register_candidate (in p_id_people int, in p_nationality varchar(2), in p_pesel varchar(11), in p_email_address varchar(256), in p_phone_number varchar(20), in p_address varchar(256))
begin
	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;
	
	start transaction;

	insert into contact_info (id_people, email_address, phone_number, address) values (p_id_people, p_email_address, p_phone_number, p_address);
	insert into sensitive_info (id_people, pesel, nationality) values (p_id_people, p_pesel, p_nationality);

	commit;
end //

create procedure login_user(in p_login varchar(32), in p_password varchar(255), in p_ip_address binary(4), out p_role varchar(20), out p_person_id int, out p_success boolean)
begin
	declare v_hashed_password varchar(255);
	set v_hashed_password = lower(sha2(p_password, 256));
	if (select count(*) from system_user where login = p_login and password_hash = v_hashed_password) = 1 then
		update system_user set last_login_date = current_timestamp, last_login_ip = p_ip_address where login = p_login;
		select system_role into p_role from system_user where login = p_login;
		select id_people into p_person_id from system_user where login = p_login;
		set p_success = true;
	else
		#toDO: report incident.
		set p_success = false;
	end if;
end //

create procedure view_applications(in p_id_people int)
begin
	select p.name as "programme_name", a.status, a.submitted_at, a.processed_at, a.motivation_letter from applications a join programmes p on a.id_programme = p.id_programme where a.id_people = p_id_people;
end //

create procedure submit_application(in p_id_people int, in p_id_programme int, in p_motivation_letter text)
begin
	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;
	
	start transaction;
	if not exists (select 1 from contact_info where id_people = p_id_people) then
		signal sqlstate '45000' set message_text = 'User submitted application but doesn''t have contact info!';
	end if;
	
	insert into applications (id_people, id_programme, motivation_letter) values (p_id_people, p_id_programme, p_motivation_letter);
	commit;
end //

create procedure approve_application(in p_id_application int, in p_id_employee int)
begin
	declare v_id_programme int;
	declare v_new_index varchar(20);
	declare v_id_people int;
	declare v_is_student int;
	declare v_id_student int;
	declare v_first_semester_id int;

	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;
	
	if (select status from applications where id_application = p_id_application) != 'pending' then
		signal sqlstate '45000' set message_text = 'Application already processed';
	end if;
	
	select id_programme, id_people into v_id_programme, v_id_people from applications where id_application = p_id_application;	

	start transaction;
	select count(*) into v_is_student from students where id_people = v_id_people;

	if v_is_student = 0 then
		select generate_index_number(v_id_programme) into v_new_index;
		call register_student(v_id_people, v_new_index);
	else
		update system_user set system_role = 'student' where id_people = v_id_people;
	end if;

	select id_student into v_id_student from students where id_people = v_id_people;

	select id_semester into v_first_semester_id from semesters where semester_number = 1 order by start_time desc limit 1;

	if v_first_semester_id is null then
		signal sqlstate '45000' set message_text = 'Cannot approve: No Semester 1 found in calendar';
	end if;

	insert into semester_enrollments (id_student, id_programme, id_semester, semester_number, status) values (v_id_student, v_id_programme, v_first_semester_id, 1, 'enrolled');

	update applications set status = 'approved', processed_at = current_timestamp, decision_by = p_id_employee where id_application = p_id_application;
	commit;
end //

create procedure reject_application(in p_id_application int, in p_id_employee int)
begin
	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	start transaction;
	update applications set status = 'rejected', processed_at = current_timestamp, decision_by = p_id_employee where id_application = p_id_application;
	commit;
end //

create procedure register_student (in p_id_people int, in p_index_number varchar(20))
begin
	declare v_status_id int;

	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	start transaction;
	
	if not exists (select 1 from applications where id_people = p_id_people and status = 'pending') then
		rollback;
		signal sqlstate '45000' set message_text = 'No pending application found for this person – cannot register as student';
	end if;

	select id_status into v_status_id from student_status where status_name = 'active';

	insert into students (id_people, id_status, index_number) values (p_id_people, v_status_id, p_index_number);
	update system_user set system_role = 'student' where id_people = p_id_people;

	commit;
end //

create procedure get_current_courses(in p_id_student int)
begin
	select 'current' as course_status, c.name as course_name, c.course_code, sem.name as semester_name, sem.academic_year, g.grade_value, g.corrected_grade, g.issued_at, concat(p.name, ' ', p.surname) as instructor_name from registrations r join course_groupes cg on r.id_course_groupe = cg.id_course_groupe join group_types gt on cg.id_groupe_type = gt.id_groupe_type join courses_in_cycles cic on cg.id_course_in_cycle = cic.id_course_in_cycle join courses c on cic.id_course = c.id_course join semesters sem on cic.id_semester = sem.id_semester left join grades g on g.id_registration = r.id_registration left join instructor_assignment ia on ia.id_course_groupe = cg.id_course_groupe left join employees e on ia.id_employee = e.id_employee left join people p on e.id_people = p.id_people where r.id_student = p_id_student and g.id_grade is null
	union all
	select 'completed' as course_status, c.name as course_name, c.course_code, sem.name as semester_name, sem.academic_year, g.grade_value, g.corrected_grade, g.issued_at, concat(p.name, ' ', p.surname) as instructor_name from registrations r join course_groupes cg on r.id_course_groupe = cg.id_course_groupe join group_types gt on cg.id_groupe_type = gt.id_groupe_type join courses_in_cycles cic on cg.id_course_in_cycle = cic.id_course_in_cycle join courses c on cic.id_course = c.id_course join semesters sem on cic.id_semester = sem.id_semester left join grades g on g.id_registration = r.id_registration left join instructor_assignment ia on ia.id_course_groupe = cg.id_course_groupe left join employees e on ia.id_employee = e.id_employee left join people p on e.id_people = p.id_people where r.id_student = p_id_student and g.id_grade is not null;
end //

create procedure get_eligible_courses(in p_id_student int)
begin
	select c.id_course, c.name as course_name, cic.id_course_in_cycle, cg.id_course_groupe, gt.name as group_type, cg.participants_limit - (select count(*) from registrations r where r.id_course_groupe = cg.id_course_groupe) as spots_left, se.semester_number, s.name as semester_name from semester_enrollments se join programme_courses pc on pc.id_programme = se.id_programme and pc.semester_number = se.semester_number join courses c on pc.id_course = c.id_course join courses_in_cycles cic on c.id_course = cic.id_course join course_groupes cg on cic.id_course_in_cycle = cg.id_course_in_cycle join group_types gt on cg.id_groupe_type = gt.id_groupe_type join semesters s on cic.id_semester = s.id_semester where se.id_student = p_id_student and se.status = 'enrolled' and not exists (select 1 from course_completions cc where cc.id_student = p_id_student and cc.id_course_in_cycle = cic.id_course_in_cycle) and not exists (select 1 from registrations r where r.id_student = p_id_student and r.id_course_groupe = cg.id_course_groupe);
end //

create procedure register_student_to_course(in p_id_student int, in p_id_course_groupe int)
begin
	declare v_limit int;
	declare v_current_count int;

	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	start transaction;

	select participants_limit into v_limit from course_groupes where id_course_groupe = p_id_course_groupe;

	select count(*) into v_current_count from registrations where id_course_groupe = p_id_course_groupe;

	if v_current_count >= v_limit then 
		signal sqlstate '45000' set message_text = 'Registration failed: Group is full';
	end if;

	if exists (select 1 from registrations where id_student = p_id_student and id_course_groupe = p_id_course_groupe) then
		signal sqlstate '45000' set message_text = 'Student already registered for this course groupe';
	end if;

	insert into registrations (id_student, id_course_groupe) values (p_id_student, p_id_course_groupe);

	commit;
end //

create procedure issue_grade(in p_id_registration int, in p_id_employee int, in p_grade_value varchar(8), in p_comment text)
begin
	declare v_existing_id int;
	declare v_old_grade varchar(8);

	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	select id_grade, grade_value into v_existing_id, v_old_grade from grades where id_registration = p_id_registration limit 1;

	if v_existing_id is not null then
		update grades set corrected_grade = p_grade_value, comment = concat(ifnull(comment, ''), ' | Correction: ', p_comment), is_corrected = true, issued_at = current_timestamp, id_employee = p_id_employee where id_grade = v_existing_id;
	else
		insert into grades (id_registration, id_employee, grade_value, comment, issued_at) values (p_id_registration, p_id_employee, p_grade_value, p_comment, current_timestamp);
	end if;

	commit;
end //

create procedure complete_course(in p_id_student int, in p_id_course_in_cycle int, in p_id_employee int)
begin
	declare v_id_grade int;
	declare v_is_already_completed int;

	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	select count(*) into v_is_already_completed from course_completions where id_student = p_id_student and id_course_in_cycle = p_id_course_in_cycle;

	if v_is_already_completed > 0 then
		signal sqlstate '45000' set message_text = 'Course already marked as completed for this student';
	end if;

	select g.id_grade into v_id_grade from grades g join registrations r on g.id_registration = r.id_registration join course_groupes cg on r.id_course_groupe = cg.id_course_groupe where r.id_student = p_id_student and cg.id_course_in_cycle = p_id_course_in_cycle limit 1;

	if v_id_grade is null then
		signal sqlstate '45000' set message_text = 'No grade found for this course cycle. Cannot complete.';	
	end if;

	start transaction;

	insert into course_completions (id_student, id_course_in_cycle, id_grade_final, completed_at) values (p_id_student, p_id_course_in_cycle, v_id_grade, current_date);

	commit;
end //

create procedure get_dashboard_data(in p_id_people int, out p_has_candidate_profile bool, out p_login varchar(50))
begin
	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	select exists (select * from contact_info where id_people = p_id_people) into p_has_candidate_profile;
	select login into p_login from system_user where id_people = p_id_people;
end //

create procedure process_semester_transition(in p_id_student int)
begin
	declare v_curr_prog_id int;
	declare v_curr_sem_num int;
	declare v_curr_calendar_sem_id int;
	declare v_next_calendar_sem_id int;
	declare v_has_next_level boolean;
    
	declare v_mandatory_count int;
	declare v_passed_count int;

	declare exit handler for sqlexception
	begin
		rollback;
		resignal;
	end;

	select id_programme, semester_number, id_semester into v_curr_prog_id, v_curr_sem_num, v_curr_calendar_sem_id from semester_enrollments where id_student = p_id_student and status = 'enrolled' limit 1;

	select count(*) into v_mandatory_count from programme_courses where id_programme = v_curr_prog_id and semester_number = v_curr_sem_num and is_mandatory = true;

	select count(distinct pc.id_course) into v_passed_count from course_completions cc join courses_in_cycles cic on cc.id_course_in_cycle = cic.id_course_in_cycle join programme_courses pc on cic.id_course = pc.id_course where cc.id_student = p_id_student and pc.id_programme = v_curr_prog_id and pc.semester_number = v_curr_sem_num and pc.is_mandatory = true;

	start transaction;

	if v_passed_count >= v_mandatory_count then
		update semester_enrollments set status = 'completed' where id_student = p_id_student and id_semester = v_curr_calendar_sem_id;

		set v_has_next_level = exists (
			select 1 from programme_courses where id_programme = v_curr_prog_id and semester_number = v_curr_sem_num + 1
		);

		if v_has_next_level then
			select id_semester into v_next_calendar_sem_id from semesters where semester_number = v_curr_sem_num + 1 order by start_time asc limit 1;

			if v_next_calendar_sem_id is not null then
				insert into semester_enrollments (id_student, id_programme, id_semester, semester_number, status) values (p_id_student, v_curr_prog_id, v_next_calendar_sem_id, v_curr_sem_num + 1, 'enrolled');
			else
				signal sqlstate '45000' set message_text = 'Next semester defined in curriculum but no calendar semester found';
			end if;
		else
			update students set id_status = (select id_status from student_status where status_name = 'graduated') where id_student = p_id_student;
		end if;
	else
		signal sqlstate '01000' set message_text = 'Student has not completed all mandatory courses for this semester.';
	end if;

	commit;
end //

create procedure get_applications()
begin
	select a.id_application, p.name, p.surname, pr.name as programme_name, a.submitted_at, a.motivation_letter from applications a join people p on a.id_people = p.id_people join programmes pr on a.id_programme = pr.id_programme where a.status = 'pending';
end //

create procedure get_available_programmes()
begin
	select p.id_programme, p.name as "programme_name", p.degree, p.form_of_study, d.name as "department_name", language from programmes p join departments d on p.id_department = d.id_department where p.is_offered = true;
end //

create procedure get_registrations()
begin
	select r.id_registration, cic.id_course_in_cycle, c.name as course_name, p.name, p.surname, r.id_student from registrations r join course_groupes cg on r.id_course_groupe = cg.id_course_groupe join courses_in_cycles cic on cic.id_course_in_cycle = cg.id_course_in_cycle join courses c on c.id_course = cic.id_course join students s on r.id_student = s.id_student join people p on p.id_people = s.id_people where cg.is_active = true;
end //

delimiter ;

grant
execute on function university.employee_id_from_people_id to 'app_student'@'localhost';

grant
execute on function university.student_id_from_people_id to 'app_student' @'localhost';

grant
execute on procedure university.register_user to 'app_student' @'localhost';

grant
execute on procedure university.register_candidate to 'app_student' @'localhost';

grant
execute on procedure university.login_user to 'app_student' @'localhost';

grant
execute on procedure university.view_applications to 'app_student' @'localhost';

grant
execute on procedure university.submit_application to 'app_student' @'localhost';

grant
execute on procedure university.get_current_courses to 'app_student' @'localhost';

grant
execute on procedure university.get_eligible_courses to 'app_student' @'localhost';

grant
execute on procedure university.register_student_to_course to 'app_student' @'localhost';

grant
execute on procedure university.get_dashboard_data to 'app_student' @'localhost';

grant
execute on procedure university.get_available_programmes to 'app_student' @'localhost';

grant
execute on function university.employee_id_from_people_id to 'app_admin' @'localhost';

grant
execute on function university.student_id_from_people_id to 'app_admin' @'localhost';

grant
execute on function university.generate_index_number to 'app_admin' @'localhost';

grant
execute on procedure university.register_user to 'app_admin' @'localhost';

grant
execute on procedure university.register_candidate to 'app_admin' @'localhost';

grant
execute on procedure university.login_user to 'app_admin' @'localhost';

grant
execute on procedure university.view_applications to 'app_admin' @'localhost';

grant
execute on procedure university.submit_application to 'app_admin' @'localhost';

grant
execute on procedure university.approve_application to 'app_admin' @'localhost';

grant
execute on procedure university.reject_application to 'app_admin' @'localhost';

grant
execute on procedure university.register_student to 'app_admin' @'localhost';

grant
execute on procedure university.get_current_courses to 'app_admin' @'localhost';

grant
execute on procedure university.get_eligible_courses to 'app_admin' @'localhost';

grant
execute on procedure university.register_student_to_course to 'app_admin' @'localhost';

grant
execute on procedure university.issue_grade to 'app_admin' @'localhost';

grant
execute on procedure university.complete_course to 'app_admin' @'localhost';

grant
execute on procedure university.get_dashboard_data to 'app_admin' @'localhost';

grant
execute on procedure university.process_semester_transition to 'app_admin' @'localhost';

grant
execute on procedure university.get_applications to 'app_admin' @'localhost';

grant
execute on procedure university.get_available_programmes to 'app_admin' @'localhost';

grant
execute on procedure university.get_registrations to 'app_admin' @'localhost';

grant execute on procedure university.register_user to 'app_guest'@'localhost';
grant execute on procedure university.login_user to 'app_guest'@'localhost';
