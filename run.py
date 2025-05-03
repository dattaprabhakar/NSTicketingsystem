# run.py
from app import create_app

app = create_app() # Uses default config or specify one

if __name__ == '__main__':
    # Use host='0.0.0.0' to make accessible on your network
    app.run(debug=app.config.get('ENV') == 'development', host='0.0.0.0', port=5000)