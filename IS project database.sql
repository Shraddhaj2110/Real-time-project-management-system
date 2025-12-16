--
-- PostgreSQL database dump
--

\restrict CKlzElguhMgiTF6AKbbSMazoKeT9rhomKkVHtMn6KEv6XNg0uoFeLkCqFgyHt1D

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

-- Started on 2025-12-16 13:24:53

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres_trial
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres_trial;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 216 (class 1259 OID 24592)
-- Name: project_events; Type: TABLE; Schema: public; Owner: postgres_trial
--

CREATE TABLE public.project_events (
    event_id uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    project_id text NOT NULL,
    task_id text NOT NULL,
    status text NOT NULL,
    increment_hours integer NOT NULL,
    increment_cost numeric(10,2) NOT NULL,
    planned_hours numeric(10,2),
    actual_hours numeric(10,2),
    percent_complete numeric(5,2),
    planned_cost_per_hour numeric(10,2),
    actual_cost numeric(12,2),
    ev numeric(14,2),
    pv numeric(14,2),
    spi numeric(8,4),
    cpi numeric(8,4),
    sv numeric(14,2),
    cv numeric(14,2),
    etc numeric(14,2),
    eac numeric(14,2),
    on_track_flag boolean
);


ALTER TABLE public.project_events OWNER TO postgres_trial;

--
-- TOC entry 215 (class 1259 OID 24585)
-- Name: project_events_trial; Type: TABLE; Schema: public; Owner: postgres_trial
--

CREATE TABLE public.project_events_trial (
    event_id uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    project_id text NOT NULL,
    task_id text NOT NULL,
    status text NOT NULL,
    increment_hours integer NOT NULL,
    increment_cost numeric(10,2) NOT NULL
);


ALTER TABLE public.project_events_trial OWNER TO postgres_trial;

--
-- TOC entry 4741 (class 2606 OID 24598)
-- Name: project_events project_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_trial
--

ALTER TABLE ONLY public.project_events
    ADD CONSTRAINT project_events_pkey PRIMARY KEY (event_id);


--
-- TOC entry 4739 (class 2606 OID 24591)
-- Name: project_events_trial project_events_trial_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres_trial
--

ALTER TABLE ONLY public.project_events_trial
    ADD CONSTRAINT project_events_trial_pkey PRIMARY KEY (event_id);


-- Completed on 2025-12-16 13:24:53

--
-- PostgreSQL database dump complete
--

\unrestrict CKlzElguhMgiTF6AKbbSMazoKeT9rhomKkVHtMn6KEv6XNg0uoFeLkCqFgyHt1D

