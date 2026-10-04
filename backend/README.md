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