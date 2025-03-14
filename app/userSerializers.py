def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "got_email_mob": user["got_email_mob"],
        "verified": user["verified"],
        "password": user["password"],
        "created_at": user["created_at"],
        "role":user["role"]
    }


def userResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


def embeddedUserResponse(user) -> dict:
    return {
        "id": str(user["_id"]),
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
    }


def userListEntity(users) -> list:
    return [userEntity(user) for user in users]
