import os
import json
from database.db import users_collection
from utils.encryption import hash_password, check_password

# Path for the "remember me" data file
REMEMBER_ME_PATH = "remember_me.json"

def register_user(username, password, role):
    if users_collection.find_one({'username': username}):
        return False  # User already exists
    hashed_pw = hash_password(password)
    users_collection.insert_one({'username': username, 'password': hashed_pw, 'role': role})
    return True

def login_user(username, password):
    user = users_collection.find_one({'username': username})
    if user and check_password(user['password'], password):
        return user
    return None

def reset_password(username, new_password):
    hashed_pw = hash_password(new_password)
    result = users_collection.update_one({'username': username}, {'$set': {'password': hashed_pw}})
    return result.modified_count > 0  # Returns True if the password was updated

def save_remember_me(username):
    with open(REMEMBER_ME_PATH, "w") as file:
        json.dump({"username": username}, file)
def change_password(username, old_password, new_password):
    # Retrieve the user from the database
    user = users_collection.find_one({'username': username})

    # Check if the old password matches the stored password
    if user and check_password(user['password'], old_password):
        # Old password matches, hash the new password
        hashed_pw = hash_password(new_password)
        # Update the password in the database
        result = users_collection.update_one(
            {'username': username}, 
            {'$set': {'password': hashed_pw}}
        )
        return result.modified_count > 0  # Return True if password was successfully updated
    else:
        return False  # Old password does not match


def get_remember_me():
    if os.path.exists(REMEMBER_ME_PATH):
        with open(REMEMBER_ME_PATH, "r") as file:
            return json.load(file).get("username")
    return None

def clear_remember_me():
    if os.path.exists(REMEMBER_ME_PATH):
        os.remove(REMEMBER_ME_PATH)
