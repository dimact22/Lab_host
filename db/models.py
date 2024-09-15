def user_serializer(user) -> dict:
    return {
        'id': str(user["_id"]),
        'name': user["name"],
        'email': user["email"],
        "password": user["password"],
        "ort": user["ort"]
            
        
    }


def users_serializer(users) -> list:
    return [user_serializer(user) for user in users]
