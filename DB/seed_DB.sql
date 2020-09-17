-- !!! consider creating functions for adding dynamic tables (bible, bible_cleaned, bible_tokens, commentaries, infographics etc)
--		so that their schema can be stored in this files even though actual tables are not created in seed.
-- 		If doing that, then these fuctions should be revoked from python code for creating dynamic tables, just by passing required table names


-- <<<<<<<<<<<<<<< content tables mainly used by VO ( some are used by AgMT as well) >>>>>>>>>>>>>>>>>>>>


CREATE TABLE public.languages (
    language_id bigint NOT NULL,
    language_code text,
    language_name text,
    local_script_name text,
    script text,
    script_direction text
);
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
    status boolean DEFAULT true NOT NULL,
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
    ADD CONSTRAINT sources_table_name_key UNIQUE (table_name);
ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.content_types(content_id);
ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.languages(language_id);
ALTER TABLE ONLY public.sources
    ADD CONSTRAINT sources_version_id_fkey FOREIGN KEY (version_id) REFERENCES public.versions(version_id);


CREATE TABLE public.audio_bibles (
    id bigint NOT NULL,
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
ALTER SEQUENCE public.audio_bibles_id_seq OWNED BY public.audio_bibles.id;
ALTER TABLE ONLY public.audio_bibles ALTER COLUMN id SET DEFAULT nextval('public.audio_bibles_id_seq'::regclass);
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
ALTER TABLE ONLY public.bcv_map
    ADD CONSTRAINT bcvmap_pkey PRIMARY KEY (ref_id);

-- !!!!!!! Add seed data

CREATE TABLE public.bible_books_look_up (
    book_id bigint NOT NULL,
    book_name text NOT NULL,
    book_code text NOT NULL
);
ALTER TABLE ONLY public.bible_books_look_up
    ADD CONSTRAINT biblebookslookup_pkey PRIMARY KEY (book_id);



CREATE TABLE public.bible_book_names (
    id integer NOT NULL,
    short text NOT NULL,
    abbr text,
    long text,
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

ALTER SEQUENCE public.bible_book_names_id_seq OWNED BY public.bible_book_names.id;
ALTER TABLE ONLY public.bible_book_names ALTER COLUMN id SET DEFAULT nextval('public.bible_book_names_id_seq'::regclass);
ALTER TABLE ONLY public.bible_book_names
    ADD CONSTRAINT bible_book_names_pkey PRIMARY KEY (id);
ALTER TABLE ONLY public.bible_book_names
    ADD CONSTRAINT bible_book_names_book_id_fkey FOREIGN KEY (book_id) REFERENCES public.bible_books_look_up(book_id);
ALTER TABLE ONLY public.bible_book_names
    ADD CONSTRAINT bible_book_names_language_id_fkey FOREIGN KEY (language_id) REFERENCES public.languages(language_id);



CREATE TABLE public.bible_videos (
    id integer NOT NULL,
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
ALTER SEQUENCE public.bible_videos_id_seq OWNED BY public.bible_videos.id;
ALTER TABLE ONLY public.bible_videos ALTER COLUMN id SET DEFAULT nextval('public.bible_videos_id_seq'::regclass);
ALTER TABLE ONLY public.bible_videos
    ADD CONSTRAINT bible_videos_pkey PRIMARY KEY (id);
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
    status boolean DEFAULT true NOT NULL
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
ALTER TABLE ONLY public.autographamt_users
    ADD CONSTRAINT autographamt_users_email_id_key UNIQUE (email_id);

-- !!!!! insert admin user into table as seed data



CREATE TABLE public.autographamt_organisations (
    organisation_id bigint NOT NULL,
    organisation_name text NOT NULL,
    organisation_address text NOT NULL,
    organisation_phone text NOT NULL,
    organisation_email text NOT NULL,
    verified boolean DEFAULT false,
    user_id bigint NOT NULL,
    status boolean DEFAULT true NOT NULL
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
    status boolean DEFAULT true NOT NULL
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
CREATE SEQUENCE public.translations_history_translation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.translations_history_translation_id_seq OWNED BY public.translations_history.translation_id;
ALTER TABLE ONLY public.translations_history ALTER COLUMN translation_id SET DEFAULT nextval('public.translations_history_translation_id_seq'::regclass);
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





-- <<<<<<<<<<<<<<<<<<<< SEED DATA >>>>>>>>>>>>>>>>>>>>>>>>

INSERT INTO content_types (content_type) VALUES('bible');          
INSERT INTO content_types (content_type) VALUES('translation_words');
INSERT INTO content_types (content_type) VALUES('translation_notes');
INSERT INTO content_types (content_type) VALUES('infographics');
INSERT INTO content_types (content_type) VALUES('videos');  
INSERT INTO content_types (content_type, key) VALUES('commentary','key123');


INSERT INTO roles(role_name) VALUES('m');
INSERT INTO roles(role_name) VALUES('ad');
INSERT INTO roles(role_name) VALUES('sa');
    

INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(1, 'genesis', 'gen');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(2, 'exodus', 'exo');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(3, 'leviticus', 'lev');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(4, 'numbers', 'num');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(5, 'deuteronomy', 'deu');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(6, 'joshua', 'jos');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(7, 'judges', 'jdg');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(8, 'ruth', 'rut');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(9, '1 samuel', '1sa');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(10, '2 samuel', '2sa');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(11, '1 kings', '1ki');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(12, '2 kings', '2ki');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(13, '1 chronicles', '1ch');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(14, '2 chronicles', '2ch');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(15, 'ezra', 'ezr');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(16, 'nehemiah', 'neh');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(17, 'esther', 'est');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(18, 'job', 'job');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(19, 'psalms', 'psa');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(20, 'proverbs', 'pro');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(21, 'ecclesiastes', 'ecc');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(22, 'song of solomon', 'sng');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(23, 'isaiah', 'isa');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(24, 'jeremiah', 'jer');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(25, 'lamentations', 'lam');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(26, 'ezekiel', 'ezk');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(27, 'daniel', 'dan');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(28, 'hosea', 'hos');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(29, 'joel', 'jol');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(30, 'amos', 'amo');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(31, 'obadiah', 'oba');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(32, 'jonah', 'jon');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(33, 'micah', 'mic');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(34, 'nahum', 'nam');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(35, 'habakkuk', 'hab');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(36, 'zephaniah', 'zep');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(37, 'haggai', 'hag');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(38, 'zechariah', 'zec');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(39, 'malachi', 'mal');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(40, 'matthew', 'mat');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(41, 'mark', 'mrk');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(42, 'luke', 'luk');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(43, 'john', 'jhn');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(44, 'acts', 'act');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(45, 'romans', 'rom');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(46, '1 corinthians', '1co');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(47, '2 corinthians', '2co');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(48, 'galatians', 'gal');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(49, 'ephesians', 'eph');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(50, 'philippians', 'php');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(51, 'colossians', 'col');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(52, '1 thessalonians', '1th');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(53, '2 thessalonians', '2th');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(54, '1 timothy', '1ti');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(55, '2 timothy', '2ti');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(56, 'titus', 'tit');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(57, 'philemon', 'phm');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(58, 'hebrews', 'heb');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(59, 'james', 'jas');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(60, '1 peter', '1pe');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(61, '2 peter', '2pe');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(62, '1 john', '1jn');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(63, '2 john', '2jn');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(64, '3 john', '3jn');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(65, 'jude', 'jud');
INSERT INTO bible_books_look_up(book_id, book_name, book_code) VALUES(66, 'revelation', 'rev');




\COPY bcv_map (ref_id,book,chapter,verse) FROM 'bcv_map.csv' DELIMITER ',' CSV HEADER;

\COPY languages (language_id,language_code,language_name) FROM 'languages.csv' DELIMITER ',' CSV HEADER;