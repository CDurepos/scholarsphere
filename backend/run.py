import sys
from pathlib import Path

# Ensure project root is on sys.path so "backend" module can be imported
backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
  sys.path.insert(0, str(project_root))

from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
