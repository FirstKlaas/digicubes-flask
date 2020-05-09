import json


def increase_build_version():
    data = None
    with open("digicubes_flask/version.json") as f:
        data = json.load(f)

    data["version"][2] += 1
    with open("digicubes_flask/version.json", "w") as f:
        json.dump(data, f, indent=2)    

if __name__ == "__main__":
    increase_build_version()