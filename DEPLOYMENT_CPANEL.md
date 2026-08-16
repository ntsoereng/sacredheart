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
DJANGO_ENVIRONMENT=production
ALLOWED_HOSTS=school.example.org,www.school.example.org
CSRF_TRUSTED_ORIGINS=https://school.example.org,https://www.school.example.org
```

Generate a unique production secret key in the application virtual environment:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Never copy the local development `SECRET_KEY` or commit the production `.env`.

For application confirmation emails, configure the `EMAIL_*` values from
`.env.example` with a dedicated school mailbox. Prefer an app password or
mailbox-specific credential, keep TLS enabled on port 587 (or SSL on port 465,
but never both), and make `DEFAULT_FROM_EMAIL` an address authorised by that
SMTP account. Do not enter mail credentials in Django Admin or Site Settings.

## 3. Install the application

Activate the virtual environment using the command shown by cPanel, then run:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

The application refuses to start when `DJANGO_ENVIRONMENT=production` is paired
with debug mode, insecure cookies, disabled HTTPS redirects, or disabled HSTS.
This prevents an accidentally copied development configuration from silently
going live.

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

Configure Apache to reject request bodies larger than 10 MiB and apply an
additional IP-based request limit to `/staff/login/`, `/staff/access-request/`,
`/admissions/`, `/contact/`, and `/alumni/share/`. The application also throttles
these endpoints, but the web-server limit rejects abusive traffic before Python
allocates memory. Keep `DJANGO_RATELIMIT_TRUSTED_PROXY_DEPTH=0` unless a known
reverse proxy sits directly in front of Passenger; set it to the exact number
of trusted proxies so attackers cannot spoof `X-Forwarded-For`.

Create a private cache directory outside `public_html`, writable only by the
application account, and set `DJANGO_CACHE_LOCATION` to it. The shared cache
makes rate limits consistent across Passenger worker processes.

### Minimise server-identifying response headers

Django removes optional application/runtime-identifying headers. LiteSpeed,
Apache, and Passenger can add their own headers after Django has returned the
response, so they must also be configured at the hosting layer.

Copy the safe per-directory rules into the domain's document root, merging
them with any cPanel-generated Passenger rules already present:

```bash
cp deployment/application.htaccess /home/USERNAME/public_html/.htaccess.security
```

Do not replace the live `.htaccess` file with that command. Open both files and
copy the directives from `.htaccess.security` into the live `.htaccess`, then
remove `.htaccess.security`. This preserves cPanel's application mapping. The
rules suppress server-generated signatures, directory listings, and common
`X-Powered-By`-style headers when `mod_headers` is available.

The production domain currently responds through LiteSpeed. The supplied
header rule asks LiteSpeed to remove its `Server` field at the domain level.
If the hosting configuration overrides per-directory header rules, ask the
hosting administrator to open LiteSpeed WebAdmin and select **Configuration →
Server → General → Server Signature → Hide Full Header**. They should also
enable **Hide Error Page Signature**, then restart LiteSpeed gracefully.

If the host switches back to Apache, its `Server` header is controlled by the
server-wide `ServerTokens` directive. In WHM, ask the hosting administrator to
set:

```apache
ServerTokens Prod
ServerSignature Off
PassengerShowVersionInHeader off
PassengerFriendlyErrorPages off
```

`ServerTokens Prod` removes Apache version, operating-system, and module
details, although standard Apache still identifies the product as `Apache`.
If the hosting provider permits a server-wide `mod_headers` rule, they can use
`Header always unset Server` to remove the field entirely. Passenger's version
setting hides its version but may still identify the product, so the
`.htaccess` `X-Powered-By` removal remains useful on either web server.

After restarting Passenger and gracefully restarting LiteSpeed when its global
setting changed, verify both a Django page and a web-server-generated 404
because headers can differ by response source:

```bash
curl -sSIk https://school.example.org/
curl -sSIk https://school.example.org/a-file-that-does-not-exist
```

Confirm that `X-Powered-By` is absent and, where the host supports full header
hiding, that `Server` is absent. Header minimisation reduces passive
fingerprinting but does not replace patching, access controls, rate limits, or
the other security measures in this guide.

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
