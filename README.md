# Sacred Heart High School Website

A secure, responsive school website and staff content-management portal built for Sacred Heart High School. The platform brings public communication, admissions, recruitment, events, news, staff profiles, and day-to-day content administration into one maintainable Django application.

## Project overview

The website serves two audiences:

- **Visitors, learners, parents/guardians, alumni, and prospective staff** receive a polished public experience with school information, admissions, news, events, vacancies, subjects, activities, and contact details.
- **Authorised school staff** receive a permission-aware portal for reviewing applications, managing public content, responding to enquiries, moderating alumni stories, and maintaining site settings.

The application is designed for deployment on cPanel with Phusion Passenger, MySQL/MariaDB, WhiteNoise, and Apache-served media.

## Features

### Public website

- Responsive, mobile-first interface with accessible navigation and keyboard-friendly controls
- School homepage with configurable branding, hero content, announcements, featured events, activities, news, alumni stories, and principal welcome
- About, donations, privacy, and terms pages
- Academic subject directory and subject detail pages
- Staff directory with principal highlighting and subject relationships
- News and events publishing with featured content and rich-text support
- Extracurricular activities and achievements showcase
- Public vacancy listings that automatically hide drafts, filled roles, closed roles, and expired opportunities
- Alumni Corner with moderated community submissions
- Contact form and configurable Google Maps embed
- Cross-content website search
- XML sitemap, robots.txt, canonical URLs, Open Graph metadata, and structured data
- Responsive image handling and protected media storage

### Admissions workflow

- Admissions opening and closing controlled by authorised staff
- Structured learner and parent/guardian application form
- Lesotho district selection with support for applicants living outside Lesotho
- Automatically generated application reference numbers
- Privacy-conscious confirmation page and email receipt
- Staff application queue with status filtering and search
- Application review statuses, attributed internal notes, reviewer tracking, and timestamps
- Permission-protected CSV export with spreadsheet-formula injection protection

### Staff portal and CMS

- Dedicated staff authentication and access-request workflow
- New access requests create inactive accounts and profiles pending approval
- Permission-aware dashboard that prioritises:
  1. New and in-review applications
  2. Upcoming events, with recent-event fallback
  3. Active vacancies
  4. Unread contact messages
- Compact navigation grouped into **Daily work** and **Website** responsibilities
- Live attention badges displayed only when action is required
- Content management for news, events, vacancies, subjects, staff profiles, and activities
- Homepage announcement and site-wide settings management
- Alumni story review and publication controls
- Fine-grained Django model permissions for viewing, adding, and editing content
- Permission-scoped database queries to prevent unauthorised draft or personal-data disclosure

## Security implementation

Security is treated as part of the application architecture rather than an afterthought.

- Model-level staff permissions and staff-status enforcement on protected routes
- Permission-filtered dashboard, navigation, context processors, and content queries
- CSRF protection across all state-changing forms
- Secure authentication redirects and Django password validation
- Anonymous request throttling for:
  - Staff login
  - Staff access requests
  - Admissions submissions
  - Contact messages
  - Alumni story submissions
- Shared filesystem cache for consistent rate limits across Passenger workers
- Fail-closed production configuration that rejects debug mode, insecure cookies, disabled HTTPS redirects, or disabled HSTS
- HTTPS redirects, HSTS, secure session and CSRF cookies, HTTP-only CSRF cookies, and an eight-hour session lifetime
- Nonce-based Content Security Policy with no unsafe inline JavaScript
- Restrictive Permissions-Policy for unused browser capabilities
- Clickjacking protection through `frame-ancestors 'none'` and `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff` and a strict referrer policy
- Rich-text sanitisation with `nh3` before trusted HTML rendering
- Randomised uploaded-media filenames and an image-only storage policy
- Apache media rules that block executable uploads and directory indexing
- CSV formula neutralisation for exported user-controlled data
- Current Django security patch release

## UX and accessibility improvements

- Mobile-first layouts across public and staff-facing pages
- Clear information hierarchy for operational and occasional staff tasks
- Compact portal navigation with icons, group labels, active-page state, and actionable badges
- Dropdown and mobile navigation implemented without runtime expression evaluation, keeping it compatible with strict CSP
- Outside-click and Escape-key dropdown dismissal
- Accessible labels, focus indicators, skip navigation, semantic regions, and ARIA state attributes
- Consistent parent/guardian terminology throughout admissions
- Graceful empty states and recent-event fallback on the dashboard
- Protected document-level horizontal overflow while retaining intentional table scrolling
- Reduced-motion support

## Technology stack

- **Backend:** Python 3.12+, Django 6.0.8
- **Database:** MySQL or MariaDB
- **Frontend:** Django templates, Tailwind CSS 4, vanilla JavaScript
- **Security and content:** nh3, Pillow
- **Static files:** WhiteNoise
- **Production hosting:** cPanel and Phusion Passenger
- **Email:** SMTP with TLS or SSL

## Project structure

```text
apps/
├── academics/    # Subjects and curriculum content
├── accounts/     # Staff authentication and access requests
├── admissions/   # Learner applications and review workflow
├── alumni/       # Alumni submissions and moderation
├── core/         # Site settings, search, contact, activities, security utilities
├── events/       # School events
├── pages/        # General content pages
├── portal/       # Staff dashboard and content-management workflows
├── posts/        # News publishing and rich-text sanitisation
├── staff/        # Staff profiles
└── vacancies/    # Recruitment content

config/           # Django settings, URL routing, WSGI, ASGI, test settings
deployment/       # Apache media-protection configuration
static/           # Tailwind source, compiled CSS, and admin assets
templates/        # Public, email, admin, and staff portal templates
```

## Local development

### 1. Create and activate a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
npm install
```

### 3. Configure the environment

Copy `.env.example` to `.env` and replace the example values:

```bash
cp .env.example .env
```

Development environments should use:

```env
DJANGO_ENVIRONMENT=development
DJANGO_DEBUG=True
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
DJANGO_SECURE_HSTS_SECONDS=0
```

Never reuse development credentials or secret keys in production.

### 4. Prepare the application

```bash
python manage.py migrate
npm run build
python manage.py collectstatic --noinput
python manage.py runserver
```

## Tests

The test configuration uses an isolated in-memory SQLite database, so it does not modify the configured MySQL database.

```bash
DJANGO_SETTINGS_MODULE=config.test_settings python manage.py test
```

The suite covers public visibility rules, staff access controls, permission boundaries, admissions, email receipts, content sanitisation, rate limiting, CSV safety, CSP nonces, security headers, dashboard behavior, and content workflows.

## Production deployment

Production deployment requires HTTPS and secure environment values. The application refuses to start when `DJANGO_ENVIRONMENT=production` is combined with unsafe core security settings.

Typical release commands are:

```bash
python -m pip install -r requirements.txt
python manage.py migrate --noinput
npm run build
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Afterward, restart the Passenger application. See [DEPLOYMENT_CPANEL.md](DEPLOYMENT_CPANEL.md) for the complete cPanel, media, cache, SSL, email, and rollout instructions.

## Operational notes

- Keep uploaded media outside the Git checkout and back it up with the database.
- Configure Apache to reject oversized requests before they reach Python.
- Store the shared rate-limit cache outside `public_html` with permissions restricted to the application account.
- Run `collectstatic` and restart Passenger after frontend, template, settings, or dependency changes.
- Run `python manage.py check --deploy` after every production release.
