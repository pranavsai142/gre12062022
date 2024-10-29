from datetime import datetime
            
def validateUser(user):
    print(user)
    if user is not None and user["exp"] >= datetime.now().timestamp():
        return True
    else:
        return False
