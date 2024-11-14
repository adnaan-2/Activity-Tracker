import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
