from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Update connection string if needed
db = client['your_database_name']  # Replace with your database name

# Specify the collection to exclude
excluded_collection = 'users'

# List all collections in the database
collections = db.list_collection_names()

# Loop through collections and delete each, except the excluded one
for collection_name in collections:
    if collection_name != excluded_collection:
        db[collection_name].drop()
        print(f"Dropped collection: {collection_name}")

print("Finished deleting collections.")