import serverless_wsgi
from run import app # This MUST point to the 'app' variable in your run.py

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)