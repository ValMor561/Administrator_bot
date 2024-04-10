CREATE DATABASE "Admin";

CREATE TABLE IF NOT EXISTS public."Scheduler"
(
    id integer NOT NULL GENERATED BY DEFAULT AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    date_post TIMESTAMP,
	text_post text,
    CONSTRAINT "Scheduler_pkey" PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."Scheduler"
    OWNER to postgres;