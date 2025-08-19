def init_security_module(app, socketio=None):
    """Initialize the Security module"""
    try:
        # Blueprint is registered in main app
        
        # Initialize WebSockets if available
        if socketio:
            try:
                from . import sockets
                sockets.init_sockets(socketio)
            except ImportError:
                print("Warning: WebSocket support not available for Security module")
        
        print("✅ Security module initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Security module: {e}")
        raise
