# 📚 PDF AI Backend

This is the backend for the [PDF AI](https://github.com/faselgodbcho/pdfai-backend/) project, built with **Django** and **Django REST Framework (DRF)**.

---

## 🚀 Getting Started (Development)

### 1. Clone the repository

```bash
git clone https://github.com/faselgodbcho/pdfai-backend.git
cd pdfai-backend
```
### 2. Install dependencies

Make sure you have Python 3.11+ and pip installed.

```bash
python -m venv .venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Apply migrations
```bash
python manage.py migrate
```

### 4. Run the development server (HTTP)
```bash
python manage.py runserver
```
## Running with HTTPS (Locally)

To serve the backend over HTTPS in local development:

### 1. Download mkcert

Follow this guide to install [mkcert](https://github.com/FiloSottile/mkcert).

### 2. Run the HTTPS wrapper script
```bash
./runhttps
```

What this does
- Creates a ./certs folder if it doesn't exist
- Generates a self-signed certificate and key using mkcert if not already present
- Starts the Django dev server over HTTPS using **runsslserver**

> ⚠️ Make sure **runhttps** is executable:
```bash
# on linux
chmod +x runhttps
```
## Environment variables

### Enable or disable debug mode (True/False)
DEBUG=True

### Your Cohere API key
COHERE_API_KEY=your_cohere_api_key_here

### Allowed hosts (comma-separated, no spaces)
ALLOWED_HOSTS=localhost,127.0.0.1

### Django secret key
SECRET_KEY=your_django_secret_key_here

### Origins allowed for CORS requests (comma-separated)
CORS_ALLOWED_ORIGINS=http://localhost:3000

### URL to your database (e.g., PostgreSQL via dj-database-url)
DATABASE_URL=postgres://user:password@localhost:5432/dbname

### Trusted origins for CSRF protection (comma-separated)
CSRF_TRUSTED_ORIGINS=https://localhost:8000,http://localhost:3000


## Tech Stack
- Python 3.11+
- Django 5+
- Django REST Framework (DRF)
- mkcert (for local HTTPS)

## Resources
Helpful documentation and tools used during development:
- [Django](https://docs.djangoproject.com/en/5.2/) — Official Django documentation
- [Django REST Framework](https://django-rest-framework.org/) — Toolkit for building Web APIs
- [Cohere Docs](https://docs.cohere.com/v2/docs/) — Embedding and command R+ API references
- [mkcert](https://github.com/FiloSottile/mkcert) — Generate trusted local SSL certificates

## Author
Made with ❤️ by [@faselgodbcho](https://github.com/faselgodbcho/)
