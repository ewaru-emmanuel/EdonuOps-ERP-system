from flask import Blueprint
from flask_socketio import SocketIO

def init_finance_module(app, socketio=None):
    """Initialize finance module"""
    from . import models, routes
    print("✅ Finance module initialized")