from flask import Flask, session
from flask_session import Session

from digicubes_flask.web import create_app


app = create_app()

#app.config["SESSION_TYPE"] = 'memcached'
#Session(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

