def user_serializer(user) -> dict:
    return {
        'id': str(user["_id"]),
        'name': user["name"],
        'email': user["email"],
        'phone': user["phone"],
        "password": user["password"]    
        
    }


def users_serializer(users) -> list:
    return [user_serializer(user) for user in users]