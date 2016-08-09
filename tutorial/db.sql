CREATE TYPE e_days AS ENUM (
  'MON',
  'TUE',
  'WED',
  'THU',
  'FRI',
  'SAT',
  'SUN'
);

CREATE TYPE e_schools AS ENUM (
  'NUS',
  'NTU'
);

CREATE TABLE public.modules
(
  id            SERIAL PRIMARY KEY,
  school        e_schools,
  year          SMALLINT NOT NULL CHECK (year > 2000 AND year < 2050),
  sem           SMALLINT NOT NULL CHECK (sem > 0 AND sem < 8),
  department    TEXT NOT NULL,
  code          TEXT NOT NULL,
  credit        REAL NOT NULL CHECK (credit >= 0 AND credit < 20),
  title         TEXT NOT NULL,
  description   TEXT NOT NULL,
  exam          TIMESTAMP,
  prerequisite  TEXT,
  preclusion    TEXT,
  availability  TEXT,
  remarks       TEXT,
  CONSTRAINT    modules__school_year_sem_code_key UNIQUE (school, year, sem, code)
);
ALTER TABLE public.modules
  OWNER TO postgres;
GRANT ALL ON TABLE public.modules TO postgres;
GRANT ALL ON TABLE public.modules TO scrapy;


CREATE TABLE lessons
(
    id              SERIAL PRIMARY KEY,
    school          e_schools,
    year            SMALLINT NOT NULL CHECK (year > 2000 AND year < 2050),
    sem             SMALLINT NOT NULL CHECK (sem > 0 AND sem < 8),
    code            TEXT NOT NULL,
    class_no        TEXT NOT NULL,
    day_text        e_days,
    lesson_type     TEXT NOT NULL,
    week_text       TEXT NOT NULL,
    venue           TEXT NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    FOREIGN KEY (school, year, sem, code) REFERENCES modules (school, year, sem, code) ON DELETE CASCADE
);
ALTER TABLE public.lessons
  OWNER TO postgres;
GRANT ALL ON TABLE public.lessons TO postgres;
GRANT ALL ON TABLE public.lessons TO scrapy;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to scrapy;