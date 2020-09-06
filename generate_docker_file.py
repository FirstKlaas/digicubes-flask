"""
Creates the Dockerfile

Author: Klaas Nebuhr
"""
from datetime import datetime
import jinja2


if __name__ == "__main__":
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("Dockerfile.in")
    outputText = template.render(today=datetime.utcnow())

    with open("Dockerfile", "wt") as f:
        f.write(outputText)
