-- Script to create the basic table strcutures and 
-- add minimal seed data for vachan-api

CREATE TABLE public.content_types (
    content_type_id SERIAL PRIMARY KEY ,
    content_type text UNIQUE NOT NULL
);

INSERT INTO content_types(content_type) VALUES('bible');
INSERT INTO content_types(content_type) VALUES('commentary');
INSERT INTO content_types(content_type) VALUES('dictionary');
INSERT INTO content_types(content_type) VALUES('infographics');
INSERT INTO content_types(content_type) VALUES('bible_video');

CREATE TABLE public.languages (
    language_id SERIAL PRIMARY KEY,
    language_code char(3) UNIQUE NOT NULL,
    language_name text NOT NULL,
    script_direction text
);

alter table languages alter column script_direction set default 'left-to-right';

\COPY languages (language_code,language_name) FROM 'languages.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE public.versions (
    version_id SERIAL PRIMARY KEY,
    version_code text NOT NULL,
    version_description text NOT NULL,
    revision integer NOT NULL,
    metadata jsonb,
    UNIQUE(version_code, revision)
);
