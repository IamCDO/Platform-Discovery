# Platform-Discovery
A website that contains student businesses and gives them the means of accessing all verified businesses directly from the website, and also allow new business send registration requests to the student affairs office.

## Render deployment

Configure the Render service with these commands so Django collects static assets during the build and Gunicorn serves the application:

- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start command: `gunicorn PAU_SBH.wsgi:application`

WhiteNoise serves the collected files from `staticfiles/`; do not commit that generated directory.
