import os
from digicubes_flask.web import create_app

app = create_app()

# gunicorn -b 0.0.0.0:5000 --workers=2 --threads=4 --worker-class=gthread wsgi:app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
