import serverless_wsgi
from run import app  # This imports the 'app' instance created in your run.py

def handler(event, context):
    # This bridges the serverless request to your Flask app
    return serverless_wsgi.handle_request(app, event, context)