from digicubes_flask import increase_minor_version, get_version_string

if __name__ == "__main__":
    version = get_version_string()
    increase_minor_version()
    print(f"{version} => {get_version_string()}")