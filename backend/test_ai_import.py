#!/usr/bin/env python3
"""
Minimal test to check AI module import
"""

try:
    print("Testing AI module import...")
    from modules.ai import init_ai_module
    print("✅ AI module imported successfully!")
    print(f"Function: {init_ai_module}")
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()



