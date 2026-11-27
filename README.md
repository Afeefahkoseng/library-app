# Library Borrowing System

![Tests](https://github.com/Afeefahkoseng/library-app/actions/workflows/ci.yml/badge.svg)

A small Django web app for browsing library books and borrowing them. It is a practice project built while following CS50's Web Programming with Python and JavaScript, **Week 7 (Testing, CI/CD)** and **Week 8 (Scalability and Security)**. The app itself is deliberately simple so the focus stays on testing, automation, security and caching.

## Borrowing rules

- A member can borrow **at most 3 books** at a time.
- A book **cannot be borrowed when no copies are left**. Available copies = total copies - members currently borrowing it.
- A member who already has a book is not offered it again in the borrow form.

## Pages

| URL | What it does |
|---|---|
| `/books/` | List all books and how many copies are available (cached for 30 seconds) |
| `/books/<id>` | Book details, current borrowers and the borrow form |
| `/books/<id>/borrow` | Borrow action (POST only) |
| `/admin/` | Add books and members (requires the superuser account) |

The root URL `/` redirects to `/books/`.

## Getting started

Requirements: Python 3.11 or newer, Git. Chrome is needed only for the Selenium tests and Docker Desktop only for the Docker setup.

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database and an admin account
python manage.py migrate
python manage.py createsuperuser

# 4. Run the server
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ to add a few books and members, then http://127.0.0.1:8000/books/ to browse and borrow.

## Running the tests

```bash
python manage.py test
```

This runs **21 tests** and should end with `OK`:

| File | Tests | What it covers |
|---|---|---|
| `tests1.py` | 4 | `unittest` checks of the borrowing rule (`books/rules.py`) |
| `books/tests.py` | 17 | Models, pages, borrowing rules, XSS escaping, CSRF protection and cache headers |

Browser tests with Selenium run separately (they open Chrome and click through a small page, `selenium_tests/days.html`):

```bash
python selenium_tests/tests.py
```

Earlier learning steps are also kept in the repo: `assert_demo.py` (plain `assert`), and `tests0.py` with `tests0.sh` (test function run from a shell script).

## Continuous integration

`.github/workflows/ci.yml` runs on every push. GitHub starts an Ubuntu machine, installs Python 3.13 and the requirements, then runs `python manage.py test`. A green check in the **Actions** tab means all 21 tests passed; a red cross means a change broke something. Selenium tests are not part of CI.

## Docker

The project can run with PostgreSQL instead of SQLite using Docker Compose:

```bash
docker compose up --build
```

In a second terminal:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
```

The site is then available at http://localhost:8000/books/. Stop it with `docker compose down` (the PostgreSQL data from this setup is not kept). The app switches to PostgreSQL when the `POSTGRES_HOST` environment variable is set, which Compose does for the `web` service.

## Security (Week 8)

- **Secrets from the environment.** `SECRET_KEY` and `DEBUG` are read from environment variables. Locally nothing needs to be set (`DEBUG` defaults to on and a development key is used). With `DEBUG=0` the app refuses to start unless `SECRET_KEY` is set:

  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(50))"   # generate a key
  DEBUG=0 SECRET_KEY=<your-key> python manage.py runserver
  ```

- **Cross-site scripting (XSS).** Django templates escape user-controlled text. Tests check that a book title or member name such as `<script>alert('hi')</script>` is shown as plain text and never executed.
- **Cross-site request forgery (CSRF).** The borrow form includes a CSRF token. Tests check that a POST without a token is rejected (403), that the form contains the token, and that borrowing via a plain GET request is not possible (405).
- **SQL injection** is avoided by using the Django ORM instead of raw SQL.

## Caching (Week 8)

The book list page uses `@cache_page(30)`, so the result is stored for 30 seconds. In a local benchmark with 300 books, one uncached request took about 0.24 s and later cached requests about 0.001 s (measured with `curl`). The load test used was `ab -n 50 -c 5 http://127.0.0.1:8000/books/`, which gave about 3.9 requests per second before caching.

The trade-off is freshness: after someone borrows a book, the count on the list page can be up to 30 seconds out of date. The borrow action itself always checks the live database, so the rules are never bypassed. The book detail page is deliberately not cached because it contains a CSRF token and the current borrower list. Caching is switched off while running tests so tests cannot affect each other.

## Project structure

```text
library-app/
├── books/
│   ├── rules.py          # can_borrow(): the 3-book rule
│   ├── models.py         # Book and Member
│   ├── views.py          # index, book, borrow
│   ├── urls.py
│   ├── admin.py
│   ├── templates/books/  # layout.html, index.html, book.html
│   └── tests.py          # Django tests (models, pages, security, cache)
├── library/              # project settings and URLs
├── selenium_tests/       # browser tests (days.html, tests.py)
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── assert_demo.py, tests0.py, tests0.sh, tests1.py
├── requirements.txt
└── manage.py
```

## Known limitations

- There is no login. Anyone can borrow as any member, so this is not suitable for real use without authentication.
- The PostgreSQL password (`postgres`) in `settings.py` and `docker-compose.yml` is for local practice only.
- The original development `SECRET_KEY` is still visible in the earlier Git history. Never reuse it; generate a new one for any real deployment.
- Page styling loads fonts from Google Fonts. Offline, the browser falls back to system fonts.
