import responder
from digicubes_flask.web import create_app

api = responder.API(static_dir="files", static_route="/files")
app = create_app()

api.mount('/', app)

api.run(port=5000, address="0.0.0.0")