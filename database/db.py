from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB URI
db = client['employee_tracking']
users_collection = db['users']

# Fix existing users by adding a default 'role' field if missing
users = users_collection.find({})
for user in users:
    if "role" not in user:
        users_collection.update_one({"_id": user["_id"]}, {"$set": {"role": "user"}})
        print(f"Updated user {user['username']} with default role 'user'.")
