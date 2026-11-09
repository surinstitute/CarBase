# CarBase backend

## Deployments

The backend container applies committed Django migrations automatically before
starting Gunicorn. This is safe on every deployment because `migrate` only
applies migrations not recorded in the database. After migration, it runs
`first_run.sh` only when the configured active superuser does not exist.

Do not run `makemigrations` during deployment. Generate and commit migrations
with the corresponding model changes, then validate them in CI.

To run multiple backend replicas, apply migrations and bootstrap once through a
separate release job, then set `DISABLE_MIGRATIONS=true` on every web replica.
With this value, the container starts Gunicorn without running migrations or
`first_run.sh`.

## Environment bootstrap

After intentionally changing its OIDC or superuser configuration, run:

```sh
sh first_run.sh
```

This command requires the OIDC and superuser environment variables. It is not
needed for a new environment: the backend runs it automatically after its
first migration.

## Commercial models

`GET /api/model-commercial/` and `GET /api/model-commercial/<id>/` include
`generationCount`, `startYear`, and `endYear` for each commercial model.
The year range covers all of its base models. The count includes generations
without base models; when no base model years exist, both years are `null`.
The collection accepts `q` (case-insensitive name search), `make` (make UUID),
and `name` (case-insensitive exact name) filters.

`GET /api/model-generations/<id>/` includes a `models` list containing the
associated base models, using the same fields as `GET /api/model/`. The list is
empty if the generation has no base models. The `/api/model-gen/` route is
currently disabled.

## Safety star filter

`GET /api/models/?safety_stars=0` and `GET /api/vehicles/?safety_stars=0`
through `safety_stars=5` filter by the exact star count of the model's most
recent safety assessment. If assessments share the latest year, the program
name determines their order, as in model details. Models without assessments
are excluded. For vehicles, this filter can be combined with the existing
`safety` filter for vehicles with or without a safety package.

## Vehicle body style filter

`GET /api/vehicles/?body_style=suv` filters vehicles by the body style of their
associated base model. The filter accepts the same body style values as
`GET /api/models/` and can be combined with the other vehicle filters.
