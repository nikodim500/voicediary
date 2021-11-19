DROP TRIGGER IF EXISTS record_insert_tg ON public.record;
DROP FUNCTION IF EXISTS public.assign_record_no();
DROP TRIGGER IF EXISTS diary_insert_tg ON public.diary;
DROP FUNCTION IF EXISTS public.assign_diary_no();
DROP TABLE IF EXISTS public.record;
DROP TABLE IF EXISTS public.diary;
DROP TABLE IF EXISTS public.user;


CREATE TABLE IF NOT EXISTS public."user"
(
    user_id text COLLATE pg_catalog."default" NOT NULL,
    user_name text COLLATE pg_catalog."ru_RU.utf8" NOT NULL,
    user_login text COLLATE pg_catalog."ru_RU.utf8",
    user_pwd text COLLATE pg_catalog."ru_RU.utf8",
    created_at timestamp with time zone DEFAULT now(),
    current_diary integer,
    CONSTRAINT user_pkey PRIMARY KEY (user_id)
)
 
TABLESPACE pg_default;

CREATE SEQUENCE IF NOT EXISTS public.diary_diary_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

CREATE TABLE IF NOT EXISTS public.diary
(
    diary_id integer NOT NULL DEFAULT nextval('diary_diary_id_seq'::regclass),
    diary_no smallint NOT NULL,
    user_id text COLLATE pg_catalog."default" NOT NULL,
    diary_name text COLLATE pg_catalog."ru_UA.utf8" NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    current_record integer,
    CONSTRAINT diary_pkey PRIMARY KEY (diary_id),
    CONSTRAINT diary_user_fk FOREIGN KEY (user_id)
        REFERENCES public."user" (user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID
)

TABLESPACE pg_default;

ALTER SEQUENCE public.diary_diary_id_seq
    OWNED BY diary.diary_id;
	
CREATE INDEX IF NOT EXISTS fki_diary_user_fk
    ON public.diary USING btree
    (user_id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE SEQUENCE IF NOT EXISTS public.record_record_id_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 2147483647
    CACHE 1;

CREATE TABLE IF NOT EXISTS public.record
(
    record_id integer NOT NULL DEFAULT nextval('record_record_id_seq'::regclass),
    diary_id integer NOT NULL,
    record_no integer NOT NULL,
    record_title text COLLATE pg_catalog."ru_RU.utf8" NOT NULL,
    record_text text COLLATE pg_catalog."ru_RU.utf8",
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    changed_at timestamp with time zone,
    CONSTRAINT record_pkey PRIMARY KEY (record_id),
    CONSTRAINT record_diary_fk FOREIGN KEY (diary_id)
        REFERENCES public.diary (diary_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID
)
 
TABLESPACE pg_default;
 
ALTER SEQUENCE public.record_record_id_seq
    OWNED BY record.record_id;

 
CREATE INDEX IF NOT EXISTS fki_record_diary_fk
    ON public.record USING btree
    (diary_id ASC NULLS LAST)
    TABLESPACE pg_default;
 
CREATE OR REPLACE FUNCTION public.assign_diary_no()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
  NEW.diary_no = (SELECT COUNT(diary_id)+1 FROM diary WHERE user_id = NEW.user_id);
  RETURN NEW;
END;
$BODY$;
 
CREATE TRIGGER diary_insert_tg
    BEFORE INSERT
    ON public.diary
    FOR EACH ROW
    EXECUTE FUNCTION public.assign_diary_no();
 
CREATE OR REPLACE FUNCTION public.assign_record_no()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
  NEW.record_no = (SELECT COUNT(record_id)+1 FROM record WHERE diary_id = NEW.diary_id);
  RETURN NEW;
END;
$BODY$;
 
CREATE TRIGGER record_insert_tg
    BEFORE INSERT
    ON public.record
    FOR EACH ROW
    EXECUTE FUNCTION public.assign_record_no();
 