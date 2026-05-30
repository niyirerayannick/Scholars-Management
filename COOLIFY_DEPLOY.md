# Coolify Deployment

This project can deploy to Coolify with the included `Dockerfile`.

## Recommended Coolify Setup

1. Create a new application from this repository.
2. Choose Dockerfile build mode.
3. Set the port to `8000`.
4. Add a PostgreSQL database in Coolify and attach its `DATABASE_URL` to the app.
5. Add these environment variables:

```text
DJANGO_SECRET_KEY=<generate-a-long-random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
DATABASE_URL=<coolify-postgres-url>
```

Optional HTTPS hardening after the domain is confirmed working:

```text
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

## Notes

- The container runs migrations automatically before starting Gunicorn.
- Static files are collected at build time and served by WhiteNoise.
- SQLite is still available for local/simple use, but PostgreSQL is recommended for Coolify.
- If you test the app over plain `http://` with `DJANGO_DEBUG=False`, set
  `DJANGO_CSRF_COOKIE_SECURE=False` and `DJANGO_SESSION_COOKIE_SECURE=False`.
  Secure cookies are enabled by default outside debug mode and are only sent by
  browsers over HTTPS.
