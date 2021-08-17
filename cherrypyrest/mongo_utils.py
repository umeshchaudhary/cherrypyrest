'''
  Created on Dec 25 2017,
  @author: Umesh Chaudhary
'''

import pymongo

MONGO_CLIENTS = ['localhost:27017', ]


def new_mongo_client():
  return pymongo.MongoClient(host=MONGO_CLIENTS, tz_aware=True)


mongo_client = new_mongo_client()

def set_mongo_client(client):
  global mongo_client
  mongo_client = client


DB = mongo_client['admin']


def set_db(db):
  global DB
  DB = db

def get_db(db_name=None):
  global DB
  if not db_name:
    return DB
  DB = mongo_client[db_name]
  return DB
