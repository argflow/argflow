CREATE TABLE public.user_basic(
	id SERIAL PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE public.dataset(
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	slug TEXT UNIQUE NOT NULL,
	author INTEGER NOT NULL REFERENCES public.user_basic(id) ON DELETE CASCADE,
	description TEXT
);

CREATE TABLE public.dataset_version(
	dataset INTEGER NOT NULL REFERENCES public.dataset(id) ON DELETE CASCADE,
	uploaded_at TIMESTAMP NOT NULL,
	location TEXT UNIQUE NOT NULL,
	
	PRIMARY KEY (dataset, uploaded_at)
);

CREATE TABLE public.model_type(
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE public.model(
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
	slug TEXT UNIQUE NOT NULL,
	type INTEGER NOT NULL REFERENCES model_type(id),
	dataset INTEGER REFERENCES dataset(id) ON DELETE SET NULL,
	author INTEGER NOT NULL REFERENCES public.user_basic(id) ON DELETE CASCADE,
	description TEXT
);

CREATE TABLE public.model_version(
	model INTEGER NOT NULL REFERENCES model(id) ON DELETE CASCADE,
	uploaded_at TIMESTAMP NOT NULL,
	location TEXT UNIQUE NOT NULL,
	
	PRIMARY KEY (model, uploaded_at)
);
