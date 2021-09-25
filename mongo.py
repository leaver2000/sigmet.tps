from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
# client = MongoClient(<<MONGODB URL>>)

# client = MongoClient(
#     "mongodb+srv://python:ma0jZKaR4cCLn3JK@wild-blue-yonder.jy40m.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
# # db = client.test

# db = client.admin

client = MongoClient(
    "mongodb+srv://localhost_development:tHNJt1tL8qRHOVaK@wild-blue-yonder.jy40m.mongodb.net/database?retryWrites=true&w=majority")
db = client.admin

# Issue the serverStatus command and print the results
serverStatusResult = db.command("serverStatus")
pprint(serverStatusResult)
