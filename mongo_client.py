from pymongo import MongoClient

# свідомо ігнорую використання config файлу :)
client = MongoClient('localhost', 27017)
reviews_collection = client.obrio.appReviews

