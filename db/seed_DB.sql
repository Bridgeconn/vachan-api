-- Script to create the basic table strcutures and 
-- add minimal seed data for vachan-api

CREATE TABLE public.content_types (
    content_type_id SERIAL PRIMARY KEY ,
    content_type text UNIQUE NOT NULL
);

INSERT INTO content_types(content_type) VALUES('bible');
INSERT INTO content_types(content_type) VALUES('commentary');
INSERT INTO content_types(content_type) VALUES('dictionary');
INSERT INTO content_types(content_type) VALUES('infographic');
INSERT INTO content_types(content_type) VALUES('bible_video');

CREATE TABLE public.languages (
    language_id SERIAL PRIMARY KEY,
    language_code char(3) UNIQUE NOT NULL,
    language_name text NOT NULL,
    script_direction text DEFAULT 'left-to-right'
);


\COPY languages (language_code,language_name) FROM 'languages.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE public.licenses (
    license_id SERIAL PRIMARY KEY,
    license_code text UNIQUE NOT NULL,
    license_name text NOT NULL,
    license_text text NOT NULL,
    permissions text[],
    created_at timestamp with time zone DEFAULT NOW(),
    created_user int NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user int NULL,
    active boolean DEFAULT true NOT NULL,
    metadata jsonb NULL
);

\COPY licenses (license_code, license_name, license_text, permissions) FROM 'licenses.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE public.versions (
    version_id SERIAL PRIMARY KEY,
    version_code text NOT NULL,
    version_description text NOT NULL,
    revision integer DEFAULT 1,
    metadata jsonb,
    UNIQUE(version_code, revision)
);


CREATE TABLE public.sources (
    source_id SERIAL PRIMARY KEY,
    table_name text UNIQUE,
    year integer NOT NULL,
    license_id int REFERENCES licenses(license_id) ON DELETE CASCADE,
    content_id int NOT NULL REFERENCES content_types(content_type_id) ON DELETE CASCADE,
    language_id int NOT NULL REFERENCES languages(language_id) ON DELETE CASCADE,
    version_id int NOT NULL REFERENCES versions(version_id) ON DELETE CASCADE,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user int NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user int NULL,
    active boolean DEFAULT true NOT NULL,
    metadata jsonb NULL
);

CREATE TABLE public.bible_books_look_up (
    book_id int PRIMARY KEY,
    book_name text NOT NULL,
    book_code char(3) NOT NULL
);

\COPY bible_books_look_up (book_id,book_name, book_code) FROM 'bible_books.csv' DELIMITER ',' CSV HEADER;
