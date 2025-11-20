from werkzeug.middleware.dispatcher import DispatcherMiddleware
from Albert_Interface import dash_app
from flask import Flask

# unused base app
base_app = Flask(__name__)

dash_app = DispatcherMiddleware(base_app, {
    '/dashboard': dash_app.server
})
