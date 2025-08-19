def init_compliance_module(app, socketio=None):
    """Initialize the Compliance module"""
    try:
        # Blueprint is registered in main app
        
        # Initialize WebSockets if available
        if socketio:
            try:
                from . import sockets
                sockets.init_sockets(socketio)
            except ImportError:
                print("Warning: WebSocket support not available for Compliance module")
        
        print("✅ Compliance module initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Compliance module: {e}")
        raise
