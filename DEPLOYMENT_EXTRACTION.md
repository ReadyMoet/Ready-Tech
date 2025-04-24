

### Core Application Files
1. `app_new.py` - Main Flask application
2. `models_new.py` - Database models and queries
3. `config.py` - Configuration settings
4. `wsgi.py` - WSGI entry point

### Configuration Files
1. `Procfile` with content: `web: gunicorn app_new:app --bind 0.0.0.0:$PORT`
2. `runtime.txt` with content: `python-3.9.18`
3. `gunicorn_config.py` - Gunicorn server configuration
4. `deployment_requirements.txt` or `requirements.txt` with the following dependencies:
   ```
   Flask==2.3.3
   flask-migrate==4.0.5
   flask-sqlalchemy==3.1.1
   openai==1.6.0
   pillow==10.1.0
   psycopg2-binary==2.9.9
   requests==2.31.0
   sqlalchemy==2.0.23
   trafilatura==1.6.2
   cairosvg==2.7.0
   gunicorn==21.2.0
   python-dotenv==1.0.0
   ```

### Template Files
All HTML templates in the `/templates` directory:
- `base.html` - Base template with layout structure
- `index.html` - Homepage
- `equipment.html` - Equipment selection page
- `troubleshooting.html` - Troubleshooting workflow
- `solutions.html` - Solutions display
- `reference.html` - Reference materials
- `buddy.html` - Tech Assistant
- `qa.html` and `qa_template.html` - Problem Solver pages
- `tests.html` - Testing page

### Static Files
All static assets in the `/static` directory:
- `/static/css/style.css` - Main stylesheet
- `/static/js/` directory with all JavaScript files:
  - `main.js` - Core functionality
  - `equipment.js` - Equipment handling
  - `troubleshooting.js` - Troubleshooting workflow
  - `speech.js` - Voice control 
  - `qa.js` - Problem Solver functionality
  - `service-worker.js` - PWA offline support
  - `pwa-installer.js` - PWA installation
- `/static/images/` directory with:
  - `fulllogo.jpg` - App logo
  - `icon-192x192.png` and `icon-512x512.png` - App icons
- `/static/manifest.json` - PWA manifest

## Step-by-Step Manual Extraction (GitHub Manual Upload)

1. Clone your Replit project locally (if possible) or download individual files
2. Create a new GitHub repository
3. Upload each file in its correct directory structure:
   - Root directory: app_new.py, models_new.py, config.py, wsgi.py, Procfile, runtime.txt, etc.
   - /templates: All HTML template files
   - /static: All static asset folders and files

## Recommended Approach (Using Local Git)

If you have git installed on your local machine and have cloned your Replit project:

1. Navigate to your project directory
2. Run the deploy_to_render.sh script which will:
   - Add all essential files to git
   - Commit changes
   - Prompt you to push to GitHub (requires remote setup)

## Environment Variables for Render Deployment

Configure these environment variables in your Render dashboard:
```
DATABASE_URL=postgresql://username:password@hostname:port/database_name
OPENAI_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=a_random_secret_key_for_flask
PORT=10000 (or leave blank to let Render assign one)
FLASK_ENV=production
```

## Deployment Steps Summary

1. Extract all files maintaining directory structure
2. Create GitHub repository with all extracted files
3. Connect GitHub repo to Render
4. Configure environment variables in Render
5. Set Build Command: `pip install -r requirements.txt`
6. Set Start Command: `gunicorn app_new:app --bind 0.0.0.0:$PORT`
7. Deploy the service
8. Visit `/api/db-migrate` endpoint once to initialize the database

Refer to DEPLOYMENT_GUIDE.md for detailed deployment instructions and troubleshooting.
