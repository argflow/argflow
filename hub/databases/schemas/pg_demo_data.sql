
INSERT INTO public.model_type (name) VALUES ('CNN');
INSERT INTO public.model_type (name) VALUES ('Bayesian Network');

INSERT INTO public.user_basic (username, password) VALUES ('test user', 'some hash');

INSERT INTO public.dataset (name, slug, author, description) VALUES ('Test dataset', 'test-dataset', 1, 'blah blah desc');
INSERT INTO public.dataset_version (dataset, uploaded_at, location) VALUES (1, NOW() - INTERVAL '1 DAY', 'test location 1');
INSERT INTO public.dataset_version (dataset, uploaded_at, location) VALUES (1, NOW(), 'test location 2');

INSERT INTO public.model (name, slug, type, author, dataset, description) VALUES ('Test CNN', 'test-cnn', 1, 1, 1, 'Demo dataset desc');
INSERT INTO public.model_version (model, uploaded_at, location) VALUES (1, NOW(), 'model test location 1');
