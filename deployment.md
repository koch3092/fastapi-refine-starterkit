# FastAPI Refine Starterkit - Deployment

This project can be deployed with Docker Compose to a remote server. The default
stack contains Postgres, MinIO, the FastAPI backend, the Refine frontend, and
Adminer. HTTPS termination and public routing are intentionally left to your own
infrastructure, such as Nginx, Caddy, a cloud load balancer, or an existing
platform gateway.

## Preparation

* Have a remote server ready.
* Install Docker Engine and the Docker Compose plugin.
* Point your DNS records to the server or load balancer.
* Create a production `.env` from `.env.example` and replace all placeholder
  secrets.

## Environment Variables

Set `ENVIRONMENT` to the target environment:

```bash
export ENVIRONMENT=production
```

Set `DOMAIN` to your application domain:

```bash
export DOMAIN=example.com
```

Important variables:

* `PROJECT_NAME`: API docs and email display name.
* `STACK_NAME`: Docker Compose project identity.
* `FRONTEND_HOST`: public frontend origin used by backend CORS.
* `BACKEND_CORS_ORIGINS`: comma-separated list of allowed CORS origins.
* `SECRET_KEY`: token signing secret.
* `FIRST_SUPERUSER`: first administrator email.
* `FIRST_SUPERUSER_PASSWORD`: first administrator password.
* `POSTGRES_SERVER`: Postgres hostname. Use `db` for the bundled container.
* `POSTGRES_PORT`: Postgres port.
* `POSTGRES_DB`: application database name.
* `POSTGRES_USER`: Postgres user.
* `POSTGRES_PASSWORD`: Postgres password.
* `S3_INTERNAL_ENDPOINT_URL`: backend-to-S3 endpoint, for example
  `http://minio:9000`.
* `S3_PUBLIC_ENDPOINT_URL`: browser-facing S3 endpoint used in presigned URLs.
* `S3_ACCESS_KEY`: S3 or MinIO access key.
* `S3_SECRET_KEY`: S3 or MinIO secret key.
* `S3_BUCKET`: asset bucket name.
* `SENTRY_DSN`: optional Sentry DSN.

Generate strong secrets with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Deploy with Docker Compose

Copy the project to the server, create `.env`, then start the production compose
file:

```bash
docker compose -f docker-compose.yml up -d --build
```

The production compose file does not publish public ports by default. Put your
own reverse proxy or platform gateway on the same Docker network and route:

* frontend host to `frontend:80`
* backend API host to `backend:8000`
* MinIO API host to `minio:9000`, if browser uploads should use bundled MinIO
* MinIO console host to `minio:9001`, only when explicitly needed

Adminer is included for operational convenience but should not be exposed
publicly without strong access controls.

If you want a direct-port deployment instead of a reverse proxy, add a
production-specific compose override that publishes only the services you need.
Use `docker-compose.override.yml` as a local-development reference, not as a
production file, because it runs the backend with reload settings.

## Frontend API URL

The frontend image is built with:

```yaml
VITE_API_URL=https://api.${DOMAIN}
```

If your deployment uses a different API origin, override that build argument in
your production compose override and keep `FRONTEND_HOST` /
`BACKEND_CORS_ORIGINS` in sync.

## Local URLs

When running the default local compose setup with `docker-compose.override.yml`,
the useful URLs are:

* Frontend: `http://localhost:5173`
* Backend API docs: `http://localhost:8000/docs`
* Backend API base URL: `http://localhost:8000`
* Adminer: `http://localhost:8080`
* MinIO API: `http://localhost:9000`
* MinIO console: `http://localhost:9001`
