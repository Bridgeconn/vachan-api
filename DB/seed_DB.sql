-- ??? Are the functions written by you, Revant?
-- 		- create_bible_table
-- 		- insert_bible_data
-- 		- make_bible_tables
-- ??? Are they being used now? Or was this part of schema alterration we did before?
-- !!! consider creating functions like these for adding dynamic tables (bible, bible_cleaned, bible_tokens, commentaries, infographics etc)
--		so that their schema can be stored in this files even though actual tables are not created in seed.
-- 		If doing that, then these fuctions should be revoked from python code for creating dynamic tables, just by passing required table names

CREATE FUNCTION public.create_bible_table(t_name character varying) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
EXECUTE FORMAT('
   CREATE TABLE IF NOT EXISTS %I (
    book_id int8 PRIMARY KEY REFERENCES bible_books_look_up(book_id),
    usfm_text text,
    json_text text
   )', t_name);

END
$$;


CREATE FUNCTION public.insert_bible_data(t_name character varying, src_id bigint) RETURNS void
    LANGUAGE plpgsql
    AS $$
declare  
   bible_text json;
   _key   text;
   _value text;
   b_id integer;
begin
    SELECT cast(usfm_text as json) into bible_text from sources where source_id =src_id;
    FOR _key, _value IN
       SELECT * FROM json_each_text(bible_text->'parsedJson')
    loop
    	select book_id into b_id from bible_books_look_up bblu where book_code = _key;
        EXECUTE FORMAT('INSERT INTO %I (book_id,usfm_text,json_text) VALUES (%s,%L,%L);', t_name,b_id,bible_text->'usfm'->>_key,_value);
    END LOOP;
END
$$;

CREATE FUNCTION public.make_bible_tables() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
  row        record;
  table_name        text;
BEGIN
  FOR row IN select s.source_id, s.table_name,s.usfm_text::json from sources s inner join content_types t on s.content_id= t.content_id where t.content_type='bible' LOOP
    if (row.table_name != '''') then 
      perform create_bible_table(row.table_name);
      perform insert_bible_data(row.table_name,row.source_id);
    end if;
  END LOOP;
END
$$;



-- <<<<<<<<<<<<<<< content tables mainly used by VO ( some are used by AgMT as well) >>>>>>>>>>>>>>>>>>>>


CREATE TABLE public.languages (
    language_id bigint NOT NULL,
    language_code text,
    language_name text,
    local_script_name text,
    script text,
    script_direction text
);
CREATE SEQUENCE public.languages_languageid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.languages_languageid_seq OWNED BY public.languages.language_id;
ALTER TABLE ONLY public.languages ALTER COLUMN language_id SET DEFAULT nextval('public.languages_languageid_seq'::regclass);
ALTER TABLE ONLY public.languages
    ADD CONSTRAINT languages_pkey PRIMARY KEY (language_id);
-- !!!! add seed data

CREATE TABLE public.content_types (
    content_id bigint NOT NULL,
    content_type text,
    key text
);
CREATE SEQUENCE public.contenttype_contentid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.contenttype_contentid_seq OWNED BY public.content_types.content_id;
ALTER TABLE ONLY public.content_types ALTER COLUMN content_id SET DEFAULT nextval('public.contenttype_contentid_seq'::regclass);
ALTER TABLE ONLY public.content_types
    ADD CONSTRAINT contenttype_pkey PRIMARY KEY (content_id);

-- !!!! add seed data


CREATE TABLE public.versions (
    version_id integer NOT NULL,
    version_code text NOT NULL,
    version_description text NOT NULL,
    revision text NOT NULL,
    metadata jsonb
);
CREATE SEQUENCE public.versions_version_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.versions_version_id_seq OWNED BY public.versions.version_id;
ALTER TABLE ONLY public.versions ALTER COLUMN version_id SET DEFAULT nextval('public.versions_version_id_seq'::regclass);
ALTER TABLE ONLY public.versions
    ADD CONSTRAINT versions_pk PRIMARY KEY (version_id);



CREATE TABLE public.sources (
    source_id bigint NOT NULL,
    table_name text,
    year integer NOT NULL,
    license text DEFAULT 'CC BY SA'::text,
    content_id bigint NOT NULL,
    language_id bigint NOT NULL,
    created_at_date timestamp with time zone DEFAULT ('now'::text)::timestamp(2) with time zone,
    status boolean,
    version_id bigint,
    metadata jsonb
);
CREATE SEQUENCE public.sources_source_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.sources_source_id_seq OWNED BY public.sources.source_id;
ALTER TABLE ONLY public.sources ALTER COLUMN source_id SET DEFAULT nextval('public.versions_version_id_seq'::regclass);
ALTER TABLE ONLY public.sources
  ADD CONSTRAINT versions_pkey PRIMARY KEY (source_id);
ALTER TABLE ONLY public.sources
    ADD CONSTRAINT versions_table_name_key UNIQUE (table_name);
ALTER TABLE ONLY public.sources
    ADD CONSTRAINT versions_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.content_types(content_id);
ALTER TABLE ONLY public.sources
    ADD CONSTRAINT versions_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.languages(language_id);


CREATE TABLE public.audio_bibles (
    audio_bible_id bigint NOT NULL,
    source_id bigint NOT NULL,
    name text NOT NULL,
    url text NOT NULL,
    books jsonb,
    format text NOT NULL,
    status boolean DEFAULT true NOT NULL
);
CREATE SEQUENCE public.audio_bibles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.audio_bibles_id_seq OWNED BY public.audio_bibles.audio_bible_id;
ALTER TABLE ONLY public.audio_bibles ALTER COLUMN audio_bible_id SET DEFAULT nextval('public.audio_bibles_id_seq'::regclass);
ALTER TABLE ONLY public.audio_bibles
    ADD CONSTRAINT audio_bibles_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.audio_bibles
    ADD CONSTRAINT audio_bibles_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(source_id);


CREATE TABLE public.bcv_map (
    ref_id bigint,
    book integer,
    chapter integer,
    verse integer
);

-- !!!!!!! Add seed data

CREATE TABLE public.bible_books_look_up (
    book_id bigint NOT NULL,
    book_name text NOT NULL,
    book_code text NOT NULL
);
ALTER TABLE ONLY public.bible_books_look_up
    ADD CONSTRAINT biblebookslookup_pkey PRIMARY KEY (book_id);



CREATE TABLE public.bible_book_names (
    bible_book_name_id integer NOT NULL,
    short text,
    abbr text,
    long text NOT NULL,
    book_id bigint NOT NULL,
    language_id bigint NOT NULL
);

CREATE SEQUENCE public.bible_book_names_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.bible_book_names_id_seq OWNED BY public.bible_book_names.bible_book_name_id;
ALTER TABLE ONLY public.bible_book_names ALTER COLUMN bible_book_name_id SET DEFAULT nextval('public.bible_book_names_id_seq'::regclass);
ALTER TABLE ONLY public.bible_book_names
    ADD CONSTRAINT bible_book_names_pkey PRIMARY KEY (bible_book_name_id);
ALTER TABLE ONLY public.bible_book_names
    ADD CONSTRAINT bible_book_names_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.bible_books_look_up(book_id);
ALTER TABLE ONLY public.bible_book_names
    ADD CONSTRAINT bible_book_names_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.languages(language_id);



CREATE TABLE public.bible_videos (
    bible_video_id integer NOT NULL,
    books text NOT NULL,
    url text NOT NULL,
    title text NOT NULL,
    description text,
    theme text,
    language_id bigint NOT NULL,
    status boolean DEFAULT true NOT NULL
);
CREATE SEQUENCE public.bible_videos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.bible_videos_id_seq OWNED BY public.bible_videos.bible_video_id;
ALTER TABLE ONLY public.bible_videos ALTER COLUMN bible_video_id SET DEFAULT nextval('public.bible_videos_id_seq'::regclass);
ALTER TABLE ONLY public.bible_videos
    ADD CONSTRAINT bible_videos_pkey PRIMARY KEY (bible_video_id);
ALTER TABLE ONLY public.bible_videos
    ADD CONSTRAINT bible_videos_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.languages(language_id);







-- <<<<<<<<<<<<<<<<<AGMT TABLES>>>>>>>>>>>>>>>>>>>>

CREATE TABLE public.roles (
    role_id bigint NOT NULL,
    role_name text NOT NULL
);
CREATE SEQUENCE public.roles_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.roles_role_id_seq OWNED BY public.roles.role_id;
ALTER TABLE ONLY public.roles ALTER COLUMN role_id SET DEFAULT nextval('public.roles_role_id_seq'::regclass);
ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (role_id);
ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_role_name_key UNIQUE (role_name);

-- !!!!! Add seed data

CREATE TABLE public.autographamt_users (
    user_id bigint NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    email_id text NOT NULL,
    password_hash bytea NOT NULL,
    password_salt bytea NOT NULL,
    created_at_date timestamp with time zone,
    verification_code text NOT NULL,
    verified boolean DEFAULT false,
    role_id bigint DEFAULT 1,
    status boolean
);
CREATE SEQUENCE public.autographamt_users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.autographamt_users_user_id_seq OWNED BY public.autographamt_users.user_id;
ALTER TABLE ONLY public.autographamt_users ALTER COLUMN user_id SET DEFAULT nextval('public.autographamt_users_user_id_seq'::regclass);
ALTER TABLE ONLY public.autographamt_users
    ADD CONSTRAINT autographamt_users_password_hash_key UNIQUE (password_hash);
ALTER TABLE ONLY public.autographamt_users
    ADD CONSTRAINT autographamt_users_password_salt_key UNIQUE (password_salt);
ALTER TABLE ONLY public.autographamt_users
    ADD CONSTRAINT autographamt_users_pkey PRIMARY KEY (user_id);
ALTER TABLE ONLY public.autographamt_users
    ADD CONSTRAINT autographamt_users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(role_id);

-- !!!!! insert admin user into table as seed data



CREATE TABLE public.autographamt_organisations (
    organisation_id bigint NOT NULL,
    organisation_name text NOT NULL,
    organisation_address text NOT NULL,
    organisation_phone text NOT NULL,
    organisation_email text NOT NULL,
    verified boolean DEFAULT false,
    user_id bigint NOT NULL,
    status boolean
);
CREATE SEQUENCE public.autographamt_organisations_organisation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.autographamt_organisations_organisation_id_seq OWNED BY public.autographamt_organisations.organisation_id;
ALTER TABLE ONLY public.autographamt_organisations ALTER COLUMN organisation_id SET DEFAULT nextval('public.autographamt_organisations_organisation_id_seq'::regclass);
ALTER TABLE ONLY public.autographamt_organisations
    ADD CONSTRAINT autographamt_organisations_pkey PRIMARY KEY (organisation_id);
ALTER TABLE ONLY public.autographamt_organisations
    ADD CONSTRAINT autographamt_organisations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.autographamt_users(user_id);


CREATE TABLE public.autographamt_projects (
    project_id bigint NOT NULL,
    project_name text NOT NULL,
    source_id bigint NOT NULL,
    target_id bigint NOT NULL,
    organisation_id bigint NOT NULL,
    status boolean
);
CREATE SEQUENCE public.autographamt_projects_project_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.autographamt_projects_project_id_seq OWNED BY public.autographamt_projects.project_id;
ALTER TABLE ONLY public.autographamt_projects ALTER COLUMN project_id SET DEFAULT nextval('public.autographamt_projects_project_id_seq'::regclass);
ALTER TABLE ONLY public.autographamt_projects
    ADD CONSTRAINT autographamt_projects_pkey PRIMARY KEY (project_id);
ALTER TABLE ONLY public.autographamt_projects
    ADD CONSTRAINT autographamt_projects_organisation_id_fkey FOREIGN KEY (organisation_id) REFERENCES public.autographamt_organisations(organisation_id);
ALTER TABLE ONLY public.autographamt_projects
    ADD CONSTRAINT autographamt_projects_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(source_id);
ALTER TABLE ONLY public.autographamt_projects
    ADD CONSTRAINT autographamt_projects_target_id_fkey FOREIGN KEY (target_id) REFERENCES public.languages(language_id);


CREATE TABLE public.autographamt_assignments (
    assignment_id bigint NOT NULL,
    books text,
    user_id bigint NOT NULL,
    project_id bigint NOT NULL
);
CREATE SEQUENCE public.autographamt_assignments_assignment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.autographamt_assignments_assignment_id_seq OWNED BY public.autographamt_assignments.assignment_id;
ALTER TABLE ONLY public.autographamt_assignments ALTER COLUMN assignment_id SET DEFAULT nextval('public.autographamt_assignments_assignment_id_seq'::regclass);
ALTER TABLE ONLY public.autographamt_assignments
    ADD CONSTRAINT autographamt_assignments_pkey PRIMARY KEY (assignment_id);
ALTER TABLE ONLY public.autographamt_assignments
    ADD CONSTRAINT autographamt_assignments_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.autographamt_projects(project_id);
ALTER TABLE ONLY public.autographamt_assignments
    ADD CONSTRAINT autographamt_assignments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.autographamt_users(user_id);


CREATE TABLE public.translations (
    translation_id bigint NOT NULL,
    token text NOT NULL,
    translation text,
    senses text,
    source_id bigint NOT NULL,
    target_id bigint NOT NULL,
    updated_at timestamp with time zone DEFAULT ('now'::text)::timestamp(2) with time zone,
    user_id bigint NOT NULL
);
CREATE SEQUENCE public.translations_translation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.translations_translation_id_seq OWNED BY public.translations.translation_id;
ALTER TABLE ONLY public.translations ALTER COLUMN translation_id SET DEFAULT nextval('public.translations_translation_id_seq'::regclass);
ALTER TABLE ONLY public.translations
    ADD CONSTRAINT translations_pkey PRIMARY KEY (translation_id);
ALTER TABLE ONLY public.translations
    ADD CONSTRAINT translations_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(source_id);
ALTER TABLE ONLY public.translations
    ADD CONSTRAINT translations_target_id_fkey FOREIGN KEY (target_id) REFERENCES public.languages(language_id);
ALTER TABLE ONLY public.translations
    ADD CONSTRAINT translations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.autographamt_users(user_id);


CREATE TABLE public.translations_history (
    translation_id bigint NOT NULL,
    token text NOT NULL,
    translation text,
    senses text,
    source_id bigint NOT NULL,
    target_id bigint NOT NULL,
    updated_at timestamp with time zone DEFAULT ('now'::text)::timestamp(2) with time zone,
    user_id bigint NOT NULL
);
ALTER TABLE ONLY public.translations_history
    ADD CONSTRAINT translations_history_pkey PRIMARY KEY (translation_id);
ALTER TABLE ONLY public.translations_history
    ADD CONSTRAINT translations_history_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.sources(source_id) ON DELETE CASCADE;
ALTER TABLE ONLY public.translations_history
    ADD CONSTRAINT translations_history_target_id_fkey FOREIGN KEY (target_id) REFERENCES public.languages(language_id);
ALTER TABLE ONLY public.translations_history
    ADD CONSTRAINT translations_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.autographamt_users(user_id) ON DELETE CASCADE;


CREATE TABLE public.translation_projects_look_up (
    id bigint NOT NULL,
    translation_id bigint NOT NULL,
    project_id bigint NOT NULL
);
CREATE SEQUENCE public.translation_projects_look_up_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.translation_projects_look_up_id_seq OWNED BY public.translation_projects_look_up.id;
ALTER TABLE ONLY public.translation_projects_look_up ALTER COLUMN id SET DEFAULT nextval('public.translation_projects_look_up_id_seq'::regclass);
ALTER TABLE ONLY public.translation_projects_look_up
    ADD CONSTRAINT translation_projects_look_up_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.translation_projects_look_up
    ADD CONSTRAINT translation_projects_look_up_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.autographamt_projects(project_id);
ALTER TABLE ONLY public.translation_projects_look_up
    ADD CONSTRAINT translation_projects_look_up_translation_id_fkey FOREIGN KEY (translation_id) REFERENCES public.translations(translation_id);



