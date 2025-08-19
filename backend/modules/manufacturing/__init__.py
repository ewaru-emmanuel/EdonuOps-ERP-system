def init_manufacturing_module(app, socketio=None):
    """Initialize the Manufacturing module"""
    try:
        # Blueprint is registered in main app
        
        # Initialize WebSockets if available
        if socketio:
            try:
                from . import sockets
                sockets.init_sockets(socketio)
            except ImportError:
                print("Warning: WebSocket support not available for Manufacturing module")
        
        print("✅ Manufacturing module initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Manufacturing module: {e}")
        raise
