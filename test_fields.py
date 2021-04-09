from digicubes_flask.client import DigiCubeClient

client = DigiCubeClient()
token = client.generate_token_for("root", "digicubes")
print(token)
users = client.user_service.all(
    token.bearer_token,
    ["first_name", "last_name"]
)

for user in users:
    print(user.dict())

print(client.user_service.user_schema(token.bearer_token))
