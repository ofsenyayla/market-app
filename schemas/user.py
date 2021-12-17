def userEntity(item) -> dict:
  return {
    "id": str(item["_id"]),
    "name": item["name"],
    "username": item["username"],
    "password": item["password"],
    "email": item["email"],
    "is_staff": item["is_staff"],
  }

def usersEntity(entity) -> list:
  return [userEntity(item) for item in entity]