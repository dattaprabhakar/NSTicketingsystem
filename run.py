# run.py
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get host/port from env or use defaults
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    # Debug mode is set inside create_app based on FLASK_ENV
    app.run(host=host, port=port)