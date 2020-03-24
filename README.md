# django-react-template
A simple script to create a Django-backed React app, all in one.

# Credit
This script is based almost 100% on this walkthrough:
https://medium.com/@dakota.lillie/django-react-jwt-authentication-5015ee00ef9a

The only difference is adding the React app to the project instead of needing a separate front end.  You then just need to set your webserver to serve the app folder as static, and you're good to go.

# What it Does
This script creates a Django project, creates a React app within in (in the /app directory) and then adds basic JWT code to enable login, logout, and signup.  

# How to use
Requirements: Python and Node must already be installed.
Side effects: This will install Django and pipenv globally.

1. Place the python script in the directory that you'd like to create the app.
2. Run `python django-react-template.py name-of-project`.
3. The script then runs through installing all needed dependencies and files.
4. Configure database if not using sqlite. (optional)
5. Run `pipenv run python manage.py migrate` from the project folder.