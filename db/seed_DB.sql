-- Script to create the basic table strcutures and 
-- add minimal seed data for vachan-api

CREATE TABLE public.resource_types (
    resource_type_id SERIAL PRIMARY KEY ,
    resource_type text UNIQUE NOT NULL,
    created_user text NULL
);

ALTER SEQUENCE public.resource_types_resource_type_id_seq RESTART WITH 100000;

INSERT INTO resource_types(resource_type) VALUES('bible');
INSERT INTO resource_types(resource_type) VALUES('commentary');
INSERT INTO resource_types(resource_type) VALUES('vocabulary');
INSERT INTO resource_types(resource_type) VALUES('parascriptural');
INSERT INTO resource_types(resource_type) VALUES('audiobible');
INSERT INTO resource_types(resource_type) VALUES('signbiblevideo'); 
INSERT INTO resource_types(resource_type) VALUES('gitlabrepo'); 

CREATE TABLE public.languages (
    language_id SERIAL PRIMARY KEY,
    language_code text UNIQUE NOT NULL,
    language_name text NOT NULL,
    script_direction text,
    localscript_name text NULL,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL
);

ALTER SEQUENCE public.languages_language_id_seq RESTART WITH 100000;

CREATE EXTENSION pg_trgm;

CREATE INDEX languages_search_idx ON languages USING gin (
    language_code gin_trgm_ops, 
    language_name gin_trgm_ops, 
    (jsonb_to_tsvector('simple', metadata, '["string", "numeric"]'))
);


\COPY languages (language_code,language_name, script_direction, metadata) FROM 'csvs/consolidated_languages.csv' DELIMITER ',' CSV;

CREATE TABLE public.licenses (
    license_id SERIAL PRIMARY KEY,
    license_code text UNIQUE NOT NULL,
    license_name text NOT NULL,
    license_text text NOT NULL,
    permissions text[],
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    metadata jsonb NULL
);

ALTER SEQUENCE public.licenses_license_id_seq RESTART WITH 100000;

\COPY licenses (license_code, license_name, license_text, permissions) FROM 'csvs/licenses.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE public.versions (
    version_id SERIAL PRIMARY KEY,
    version_short_name text NOT NULL,
    version_name text NOT NULL,
    version_tag varchar(15)[] DEFAULT '{"1"}',
    metadata jsonb,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    UNIQUE(version_short_name, version_tag)
);

ALTER SEQUENCE public.versions_version_id_seq RESTART WITH 100000;

CREATE TABLE public.resources (
    resource_id SERIAL PRIMARY KEY,
    version text UNIQUE,
    resource_table text UNIQUE,
    year integer NOT NULL,
    labels text[],
    license_id int REFERENCES licenses(license_id),
    resourcetype_id int NOT NULL REFERENCES resource_types(resource_type_id),
    language_id int NOT NULL REFERENCES languages(language_id),
    version_id int NOT NULL REFERENCES versions(version_id),
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    metadata jsonb NULL
);

ALTER SEQUENCE public.resources_resource_id_seq RESTART WITH 100000;

CREATE TABLE public.bible_books_look_up (
    book_id int PRIMARY KEY,
    book_name text NOT NULL,
    book_code char(3) NOT NULL
);

\COPY bible_books_look_up (book_id,book_name, book_code) FROM 'csvs/bible_books.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE public.translation_projects(
    project_id SERIAL PRIMARY KEY,
    project_name TEXT NOT NULL,
    source_lang_id int NOT NULL
        REFERENCES languages(language_id),
    target_lang_id int NOT NULL 
        REFERENCES languages(language_id),
    source_document_format text DEFAULT 'Bible USFM',
    active boolean default true,
    metadata jsonb,
    created_user text NULL,
    created_at timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    compatible_with text[],
    UNIQUE(project_name, created_user)
);
ALTER SEQUENCE public.translation_projects_project_id_seq RESTART WITH 100000;

CREATE TABLE public.translation_sentences(
    draft_id SERIAL PRIMARY KEY,
    project_id int NOT NULL 
        REFERENCES translation_projects(project_id) ON DELETE CASCADE,
    sentence_id int NOT NULL,
    surrogate_id text,
    sentence text,
    draft text,
    draft_metadata jsonb,
    last_updated_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    UNIQUE(project_id, sentence_id)
);
ALTER SEQUENCE public.translation_sentences_draft_id_seq RESTART WITH 100000;

CREATE TABLE public.translation_memory(
    token_id SERIAL PRIMARY KEY,
    source_lang_id int NOT NULL
        REFERENCES languages(language_id),
    target_lang_id int 
        REFERENCES languages(language_id),
    source_token text NOT NULL,
    source_token_romanized text,
    source_token_metadata jsonb NULL,
    translation text,
    translation_romanized text,
    frequency int,
    UNIQUE(source_lang_id, target_lang_id, source_token, translation)
);
CREATE EXTENSION fuzzystrmatch;
CREATE INDEX token_soundex ON translation_memory (SOUNDEX(source_token_romanized));
CREATE INDEX translation_soundex ON translation_memory (SOUNDEX(translation_romanized));
ALTER SEQUENCE public.translation_memory_token_id_seq RESTART WITH 100000;

CREATE TABLE public.translation_project_users(
    project_user_id SERIAL PRIMARY KEY,
    project_id int REFERENCES translation_projects(project_id),
    user_id text NULL,
    user_role text default 'projectMember',
    metadata jsonb,
    active boolean default true,
    UNIQUE(project_id, user_id)
);

ALTER SEQUENCE public.translation_project_users_project_user_id_seq RESTART WITH 100000;

CREATE TABLE public.stopwords_look_up(
    sw_id SERIAL PRIMARY KEY,
    language_id int,
    stopword text,
    confidence float, 
    created_at timestamp with time zone DEFAULT NOW(),	
    created_user text NULL, 
    last_updated_at timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL, 
    active boolean, 
    metadata jsonb NULL, 
    UNIQUE(language_id, stopword)
);

ALTER SEQUENCE public.stopwords_look_up_sw_id_seq RESTART WITH 100000;

-- COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM PROGRAM 'awk FNR-1 ./csvs/stop_words/*.csv | cat' csv NULL AS 'NULL'
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/assamese.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/bengali.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/gujarati.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/hindi.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/kannada.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/malayalam.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/marathi.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/punjabi.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/tamil.csv' DELIMITER ',' CSV HEADER;
\COPY stopwords_look_up(language_id,stopword,confidence,created_user,last_updated_user,active) FROM 'csvs/stop_words/telugu.csv' DELIMITER ',' CSV HEADER;

CREATE TABLE public.jobs(
    job_id SERIAL PRIMARY KEY,
    user_id text NULL,
    created_time timestamp with time zone DEFAULT NOW(),
    start_time timestamp with time zone DEFAULT NOW(),	
    end_time timestamp with time zone DEFAULT NOW(),
    status text, 
    output jsonb NULL, 
    UNIQUE(job_id, user_id)
); 

ALTER SEQUENCE public.jobs_job_id_seq RESTART WITH 100000;

CREATE TABLE public.deleted_items (
    item_id  SERIAL PRIMARY KEY,
    deleted_data JSON,
    deleted_user text NULL,
    deleted_time timestamp with time zone DEFAULT NOW(),
    deleted_from text NOT NULL,
    UNIQUE(item_id)
    );

ALTER SEQUENCE public.deleted_items_item_id_seq RESTART WITH 100000;
