CREATE TABLE Course(
	course_id VARCHAR (50),
	title VARCHAR (100),
	catalog_num VARCHAR (50),
	credits VARCHAR (50),
	consent VARCHAR(50),
	location VARCHAR(50),
	course_type VARCHAR(50),
	PRIMARY KEY (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE Classroom(
	room_num VARCHAR (50),
	building VARCHAR (50),
	room_cap VARCHAR (50),
	PRIMARY KEY (room_num, building)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE Instructor(
	first_name VARCHAR (50),
	last_name VARCHAR (50),
	faculty_type VARCHAR (150),
	PRIMARY KEY (first_name, last_name)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE class_time(
	days VARCHAR (50),
	timest VARCHAR (50),
	PRIMARY KEY (days, timest)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE Section(
	class_section VARCHAR (50),
	sem VARCHAR (50),
	year VARCHAR (50),
	course_id VARCHAR (50),
	room_num VARCHAR(50),
	building VARCHAR(50),
	days VARCHAR(50),
	timest VARCHAR(50),
	classnbr VARCHAR(50),
	class_type VARCHAR(50),
	enroll_cap VARCHAR(50),
	enroll_tot VARCHAR(50),
	waitlist_cap VARCHAR(50),
	waitlist_tot VARCHAR(50),
	class_topic VARCHAR(50),
	consent VARCHAR(50),
	PRIMARY KEY (class_section, sem, year, course_id),
	FOREIGN KEY(course_id) REFERENCES Course(course_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE teaches(
	class_section VARCHAR (50),
	sem VARCHAR (50),
	year VARCHAR(50),
	course_id VARCHAR(50),
	first_name VARCHAR(50),
	last_name VARCHAR(50),
	PRIMARY KEY (class_section, sem, year, course_id, first_name, last_name),
	FOREIGN KEY(class_section, sem, year, course_id) REFERENCES Section(class_section, sem, year, course_id),
	FOREIGN KEY(first_name, last_name) REFERENCES Instructor(first_name, last_name)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE Crosslisted(
	class_section_u VARCHAR (50),
	sem_u VARCHAR (50),
	year_u VARCHAR (50),
	course_id_u VARCHAR (50),

	class_section_g VARCHAR (50),
	sem_g VARCHAR (50),
	year_g VARCHAR (50),
	course_id_g VARCHAR (50),
	PRIMARY KEY (class_section_u, sem_u, year_u, course_id_u,class_section_g, sem_g, year_g, course_id_g),
	FOREIGN KEY(class_section_u, sem_u, year_u, course_id_u) REFERENCES Section(class_section, sem, year, course_id),
	FOREIGN KEY(class_section_g, sem_g, year_g, course_id_g) REFERENCES Section(class_section, sem, year, course_id)

) ENGINE=InnoDB DEFAULT CHARSET=latin1;