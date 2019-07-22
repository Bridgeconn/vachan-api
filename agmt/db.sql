CREATE TABLE roles (
	role_id BIGSERIAL PRIMARY KEY,
	role_name TEXT UNIQUE NOT NULL
);

INSERT INTO roles (role_name) VALUES ('m');
INSERT INTO roles (role_name) VALUES ('ad');
INSERT INTO roles (role_name) VALUES ('sa');

CREATE TABLE autographamt_users (
	user_id  BIGSERIAL PRIMARY KEY,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email_id TEXT NOT NULL,
	password_hash BYTEA UNIQUE NOT NULL,
	password_salt BYTEA UNIQUE NOT NULL,
	created_at_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2),
	verification_code TEXT NOT NULL,
	verified BOOLEAN DEFAULT FALSE,
	role_id BIGINT REFERENCES roles(role_id) DEFAULT 1
);

CREATE TABLE content_types (
	content_id BIGSERIAL PRIMARY KEY,
	content_type TEXT NOT NULL
);

CREATE TABLE languages (
	language_id BIGSERIAL PRIMARY KEY,
	language_name TEXT NOT NULL,
	language_code TEXT NOT NULL,
	local_script_name TEXT NOT NULL,
	script TEXT NOT NULL,
	srcipt_direction TEXT NOT NULL,
);

CREATE TABLE bible_books_look_up (
	book_id BIGSERIAL PRIMARY KEY,
	book_name TEXT NOT NULL,
	book_code TEXT NOT NULL
);

CREATE TABLE bcv_lid_map (
	lid BIGSERIAL PRIMARY KEY,
	book INT NOT NULL,
	chapter INT NOT NULL,
	verse INT NOT NULL
);

CREATE TABLE sources (
	source_id BIGSERIAL PRIMARY KEY,
	version_content_code TEXT NOT NULL,
	version_content_description TEXT NOT NULL,
	table_name TEXT UNIQUE,
	year INT NOT NULL,
	license TEXT DEFAULT 'CC BY SA',
	revision FLOAT,
	created_at_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2),
	content_id BIGINT REFERENCES content_type(content_id) NOT NULL,
	language_id BIGINT REFERENCES languages(language_id) NOT NULL,
	usfm_text json
);

CREATE TABLE translations (
	translation_id BIGSERIAL PRIMARY KEY,
	token TEXT NOT NULL,
	translation TEXT,
	senses TEXT,
	source_id BIGINT REFERENCES sources(source_id) NOT NULL,
	target_id BIGINT REFERENCES languages(language_id) NOT NULL,
	updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2),
	user_id BIGINT REFERENCES autographamt_users(user_id) NOT NULL
);

CREATE TABLE translations_history (
	translation_id BIGSERIAL PRIMARY KEY,
	token TEXT NOT NULL,
	translation TEXT,
	senses TEXT,
	source_id BIGINT REFERENCES sources(source_id) NOT NULL,
	target_id BIGINT REFERENCES languages(language_id) NOT NULL,
	updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2),
	user_id BIGINT REFERENCES autographamt_users(user_id) NOT NULL
);

CREATE TABLE autographamt_organisations (
	organisation_id BIGSERIAL PRIMARY KEY,
	organisation_name TEXT NOT NULL,
	organisation_address TEXT NOT NULL,
	organisation_phone INT NOT NULL,
	organisation_email TEXT NOT NULL,
	verified BOOLEAN DEFAULT FALSE,
	user_id BIGINT REFERENCES autographamt_users(user_id) NOT NULL
);

CREATE TABLE autographamt_projects (
	project_id BIGSERIAL PRIMARY KEY,
	project_name TEXT NOT NULL,
	source_id BIGINT REFERENCES sources(source_id) NOT NULL,
	target_id BIGINT REFERENCES languages(language_id) NOT NULL,
	organisation_id BIGINT REFERENCES autographamt_organisations(organisation_id) NOT NULL
);

CREATE TABLE autographamt_assignments (
	assignment_id BIGSERIAL PRIMARY KEY,
	books TEXT,
	user_id BIGINT REFERENCES autographamt_users(user_id) NOT NULL,
	project_id BIGINT REFERENCES autographamt_projects(project_id) NOT NULL
);

CREATE TABLE translation_projects_look_up (
	id BIGSERIAL PRIMARY KEY,
	translation_id BIGINT REFERENCES translations(translation_id) NOT NULL,
	project_id BIGINT REFERENCES autographamt_projects(project_id) NOT NULL
);
