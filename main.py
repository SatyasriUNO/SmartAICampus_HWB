# main.py

import uvicorn
from backend.api import app

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════╗
║     Smart Campus AI Assistant                ║
║     Powered by Hindsight Memory              ║
╠══════════════════════════════════════════════╣
║  API Docs  → http://localhost:8000/docs      ║
║  Contrast  → http://localhost:8000/demo/contrast ║
║  Events    → http://localhost:8000/demo/events   ║
╚══════════════════════════════════════════════╝
    """)
    uvicorn.run(
        "backend.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
