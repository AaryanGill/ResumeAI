import serverless_wsgi
from run import app # Change 'run' to 'app' if your Flask instance is in app.py

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)