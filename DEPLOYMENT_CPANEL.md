# Deploying Sacred Heart on cPanel “Setup Python App”

This project is configured for a persistent Git checkout used as the Phusion
Passenger application root, MySQL/MariaDB, WhiteNoise static assets, and a
shared Apache-served media directory outside the repository.

## 1. Prepare cPanel

1. Create a MySQL database and user in **MySQL Databases**. Grant the user all
   privileges on that database. cPanel normally prefixes both names with the
   account username.
2. Ensure the domain has a valid SSL certificate (usually through AutoSSL).
3. Clone the repository in cPanel, preferably below your home directory rather
   than inside `public_html`, for example:

   ```text
   /home/USERNAME/repositories/sacredheart
   ```

4. Open **Setup Python App** and create an application with:
   - Python version: **3.12 or newer** (required by Django 6).
   - Application root: the cloned repository directory containing `manage.py`.
   - Application URL: the required domain or subdomain.
   - Startup file: `passenger_wsgi.py`.
   - Application entry point: `application`.

Do not clone the repository into a publicly browsable document directory unless
the cPanel application configuration fully protects that directory. A checkout
under `/home/USERNAME/repositories/` or `/home/USERNAME/apps/` is preferable.

## 2. Configure environment variables

Use cPanel’s application environment-variable controls when available. Copy the
names from `.env.example`, replacing every example value. If the hosting panel
does not expose environment controls, create `.env` in the application root and
set its permissions to `600`.

Important production values:

```text
DJANGO_DEBUG=False
ALLOWED_HOSTS=school.example.org,www.school.example.org
CSRF_TRUSTED_ORIGINS=https://school.example.org,https://www.school.example.org
```

Generate a unique production secret key in the application virtual environment:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Never copy the local development `SECRET_KEY` or commit the production `.env`.

## 3. Install the application

Activate the virtual environment using the command shown by cPanel, then run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

The compiled Tailwind stylesheet is already included in the repository; Node.js
is not required on the server unless the CSS source is changed there.

WhiteNoise serves the files collected into `STATIC_ROOT`, including Django
Admin assets. The default `staticfiles/` directory is generated, ignored by
Git, and safe to rebuild after each pull. Run `collectstatic --noinput` after
every deployment that changes CSS, JavaScript, images, or Django packages.

## 4. Configure persistent uploaded media

Media must live outside the replaceable application directory. The easiest
cPanel arrangement is a `media` directory inside the domain’s document root:

```text
/home/USERNAME/public_html/media
```

For a subdomain or addon domain, replace `public_html` with that domain’s actual
document root. Set:

```text
MEDIA_ROOT=/home/USERNAME/public_html/media
MEDIA_URL=/media/
```

Create the directory, give the cPanel account write access, and copy the
provided protection file:

```bash
mkdir -p /home/USERNAME/public_html/media
cp deployment/media.htaccess /home/USERNAME/public_html/media/.htaccess
chmod 755 /home/USERNAME/public_html/media
chmod 644 /home/USERNAME/public_html/media/.htaccess
```

Apache should serve existing files under `/media/` directly before Passenger.
Verify this by uploading an image through Django Admin and opening its `/media/`
URL. The application includes a Django media fallback for cPanel installations
that route `/media/` through Passenger. Once Apache is confirmed to serve the
directory directly, set `DJANGO_SERVE_MEDIA=False` to remove that fallback.
WhiteNoise is used only for static assets, not uploaded media.

Back up `MEDIA_ROOT` together with the MySQL database. Database backups alone do
not contain uploaded logos, photographs, or hero images.

## 5. SSL and security rollout

The example production configuration redirects to HTTPS, sets secure cookies,
and enables HSTS. Confirm HTTPS and redirect behaviour before leaving HSTS at
one year. If the first request loops between HTTP and HTTPS, confirm cPanel is
forwarding `X-Forwarded-Proto: https`; temporarily set
`DJANGO_SECURE_SSL_REDIRECT=False` only while correcting the proxy setup.

Never enable `DJANGO_DEBUG` in production. A production deployment check may
warn about host or HTTPS values until the real domain variables are loaded.

## 6. Pulling future releases

Do not make application-code changes through cPanel's File Manager because they
can conflict with later pulls. Before each release, activate the Python App
virtual environment, change into the repository, and run:

```bash
git status --short
git pull --ff-only
python -m pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check --deploy
```

`git pull --ff-only` deliberately stops instead of creating an unexpected merge
on the server. Review any local changes reported by `git status` before pulling.
The ignored `.env`, `staticfiles/`, and external `MEDIA_ROOT` are not replaced
by a normal pull.

If the site loads without styling before `collectstatic` has been run,
`WHITENOISE_USE_FINDERS=True` allows WhiteNoise to find repository static
assets as a fallback. Keep running `collectstatic` on every deployment for
compressed, cache-friendly production assets.

If cPanel provides environment-variable fields, prefer them to `.env`. If you
use `.env`, create it directly on the server after cloning; never add or commit
it. Keep its permissions at `600`.

Restart the application from **Setup Python App** after the commands complete.
Some cPanel installations also restart when `tmp/restart.txt` is touched, but
the panel's Restart action is the clearer option.

## 7. Restart and verify

Verify:

- `/` loads over HTTPS without a redirect loop.
- `/admin/` has CSS and Sacred Heart branding.
- `/static/css/output.css` returns `200` with a long cache header.
- An uploaded image under `/media/` returns `200`.
- A nonexistent media file returns `404`, not a Django debug page.
- Staff login, CSRF-protected forms, image uploads, and database writes work.
- The cPanel application error log contains no startup or permission errors.

After each release, confirm both database and media backups remain healthy.
