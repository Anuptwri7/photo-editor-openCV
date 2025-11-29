Photo Editor - Django + OpenCV (sample project)
==============================================
What you get:
- A minimal Django project (SQLite) with an `editor` app.
- Frontend (templates + JS) that shows immediate preview when selecting an image.
- Client-side sliders for Brightness and Contrast (live, using canvas pixel manipulation).
- Preset filters (Grayscale, Bright, Contrast) applied client-side instantly.
- Buttons for Sharpen and HDR that call server-side OpenCV endpoints for higher-quality processing.
How to run:
1. Create a Python virtualenv (Python 3.8+).
   python -m venv venv
   source venv/bin/activate   (or venv\Scripts\activate on Windows)
2. Install requirements:
   pip install -r requirements.txt
3. Apply migrations and runserver:
   python manage.py migrate
   python manage.py runserver
4. Open http://127.0.0.1:8000/ in your browser.
Notes:
- Client-side edits are fast and used for immediate preview. Sharpen/HDR use server-side for better results.
- This is a starting template — you can extend filters, add saving, authentication, or S3 storage.
