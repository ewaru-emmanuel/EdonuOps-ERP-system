def init_api_module(app, socketio=None):
    """Initialize the API Ecosystem module"""
    try:
        # Blueprint is registered in main app
        
        # Initialize WebSockets if available
        if socketio:
            try:
                from . import sockets
                sockets.init_sockets(socketio)
            except ImportError:
                print("Warning: WebSocket support not available for API Ecosystem module")
        
        print("✅ API Ecosystem module initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing API Ecosystem module: {e}")
        raise
