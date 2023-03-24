CREATE TABLE public.content_types (
    content_type_id SERIAL PRIMARY KEY ,
    content_type text UNIQUE NOT NULL
);

ALTER SEQUENCE public.content_types_content_type_id_seq RESTART WITH 100000;

INSERT INTO content_types(content_type) VALUES('bible');
INSERT INTO content_types(content_type) VALUES('commentary');
INSERT INTO content_types(content_type) VALUES('dictionary');
INSERT INTO content_types(content_type) VALUES('infographic');
INSERT INTO content_types(content_type) VALUES('biblevideo');
INSERT INTO content_types(content_type) VALUES('gitlabrepo'); 

CREATE TABLE public.languages (
    language_id SERIAL PRIMARY KEY,
    language_code text UNIQUE NOT NULL,
    language_name text NOT NULL,
    script_direction text,
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

CREATE TABLE public.versions (
    version_id SERIAL PRIMARY KEY,
    version_code text NOT NULL,
    version_description text NOT NULL,
    revision integer DEFAULT 1,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    UNIQUE(version_code, revision)
);

ALTER SEQUENCE public.versions_version_id_seq RESTART WITH 100000;

CREATE TABLE public.sources (
    source_id SERIAL PRIMARY KEY,
    source_name text UNIQUE,
    source_table text UNIQUE,
    year integer NOT NULL,
    license_id int REFERENCES licenses(license_id) ON DELETE CASCADE,
    content_id int NOT NULL REFERENCES content_types(content_type_id) ON DELETE CASCADE,
    language_id int NOT NULL REFERENCES languages(language_id) ON DELETE CASCADE,
    version_id int NOT NULL REFERENCES versions(version_id) ON DELETE CASCADE,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    metadata jsonb NULL
);

ALTER SEQUENCE public.sources_source_id_seq RESTART WITH 100000;

CREATE TABLE public.bible_books_look_up (
    book_id int PRIMARY KEY,
    book_name text NOT NULL,
    book_code char(3) NOT NULL
);

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

CREATE TABLE public.roles (
    role_id SERIAL PRIMARY KEY,
    role_name text NOT NULL UNIQUE,
    role_of_app text NULL,
    role_description text NULL,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    UNIQUE(role_id)
);

ALTER SEQUENCE public.roles_role_id_seq RESTART WITH 100000;

INSERT INTO roles(role_name) VALUES('SuperAdmin');
INSERT INTO roles(role_name) VALUES('VachanAdmin');
INSERT INTO roles(role_name) VALUES('AgAdmin');
INSERT INTO roles(role_name) VALUES('AgUser');
INSERT INTO roles(role_name) VALUES('VachanUser');
INSERT INTO roles(role_name) VALUES('APIUser');
INSERT INTO roles(role_name) VALUES('BcsDeveloper');

CREATE TABLE public.resource_types (
    resource_type_id SERIAL PRIMARY KEY,
    resource_type_name text NOT NULL UNIQUE,
    resource_type_description text,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    UNIQUE(resource_type_id)
);

ALTER SEQUENCE public.resource_types_resource_type_id_seq RESTART WITH 100000;

CREATE TABLE public.permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_name text NOT NULL UNIQUE,
    permission_description text,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    UNIQUE(permission_id)
);

ALTER SEQUENCE public.permissions_permission_id_seq RESTART WITH 100000;

CREATE TABLE public.apps (
    app_id SERIAL PRIMARY KEY,
    app_name text NOT NULL UNIQUE,
    default_role text NOT NULL,
    app_key text NOT NULL,
    use_for_registration boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    UNIQUE(app_id),
    CONSTRAINT fk_assocaited_role FOREIGN KEY(default_role) REFERENCES public.roles(role_name)
);
INSERT INTO apps(app_name,default_role,app_key,use_for_registration) VALUES('Autographa', 'AgUser','temp_key', true);
INSERT INTO apps(app_name,default_role,app_key,use_for_registration) VALUES('Vachan-online or vachan-app', 'VachanUser','temp_key', true);
INSERT INTO apps(app_name,default_role,app_key,use_for_registration) VALUES('VachanAdmin', 'VachanAdmin','temp_key', false);
INSERT INTO apps(app_name,default_role,app_key,use_for_registration) VALUES('API-user', 'APIUser','temp_key', true);

ALTER SEQUENCE public.apps_app_id_seq RESTART WITH 100000;

CREATE TABLE public.access_rules (
    rule_id SERIAL PRIMARY KEY,
    entitlement_id int NOT NULL,
    tag_id int NOT NULL,
    roles text[],
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    UNIQUE(entitlement_id,tag_id),
    CONSTRAINT fk_entitlement FOREIGN KEY(entitlement_id) REFERENCES public.resource_types(resource_type_id),
    CONSTRAINT fk_tag FOREIGN KEY(tag_id) REFERENCES public.permissions(permission_id)
);

ALTER SEQUENCE public.access_rules_rule_id_seq RESTART WITH 100000;

CREATE TABLE public.api_permissions_map (
    permission_map_id SERIAL PRIMARY KEY,
    api_endpoint text NOT NULL,
    method text NOT NULL,
    request_app_id int NOT NULL,
    filter_results boolean DEFAULT false NOT NULL,
    resource_type_id int NOT NULL,
    permission_id int NOT NULL,
    created_at timestamp with time zone DEFAULT NOW(),
    created_user text NULL,
    last_updated_at  timestamp with time zone DEFAULT NOW(),
    last_updated_user text NULL,
    active boolean DEFAULT true NOT NULL,
    UNIQUE(permission_map_id),
    CONSTRAINT fk_request_app FOREIGN KEY(request_app_id) REFERENCES public.apps(app_id),
    CONSTRAINT fk_resource_type FOREIGN KEY(resource_type_id) REFERENCES public.resource_types(resource_type_id),
    CONSTRAINT fk_permission FOREIGN KEY(permission_id) REFERENCES public.permissions(permission_id)
);

ALTER SEQUENCE public.api_permissions_map_permission_map_id_seq RESTART WITH 100000;

ALTER TABLE public.api_permissions_map ADD CONSTRAINT check_type CHECK (public.api_permissions_map.method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'));