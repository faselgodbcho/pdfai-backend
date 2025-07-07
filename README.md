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
