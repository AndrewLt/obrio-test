from pymongo import MongoClient

client = MongoClient('localhost', 27017)
reviews_collection = client.obrio.appReviews

