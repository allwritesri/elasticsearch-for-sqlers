from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import ConnectionError, RequestError
import time
import json
import os
import psycopg2
from psycopg2 import extras
import logging

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger.propagate = 0
# prevents handlers from being created twice
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    ch.setFormatter(formatter)

    logger.addHandler(ch)


# follow Mihai Todor's suggestion on https://stackoverflow.com/questions/48711455/create-dockerized-elasticsearch-index-using-a-python-script-running-in-docker/48712414#48712414
es = Elasticsearch(hosts=[{"host": "elasticsearch"}], retry_on_timeout=True)


for _ in range(100):
    try:
        # make sure the cluster is available
        health = es.cluster.health()
        if health["status"] == "yellow" or health["status"] == "green":
          break
    except ConnectionError:
        time.sleep(2)

print("Creating first data in cluster... (please hold on)")

path = os.path.dirname(os.path.abspath(__file__)) + '/mock-user-data.json'
with open(path) as f:
    user_data = json.load(f)



try:
# use the helpers library's Bulk API to index list of Elasticsearch docs
  resp = bulk(
  es,
  user_data,
  index = "user-000001"
  )
  print("\ncreated user data index")
except (ConnectionError) as e:
  print(e)

path = os.path.dirname(os.path.abspath(__file__)) + '/mock-tweet-data-sql-design.json'
with open(path) as f:
    tweet_data_1 = json.load(f)


try:
# use the helpers library's Bulk API to index list of Elasticsearch docs
  resp = bulk(
  es,
  tweet_data_1,
  index = "tweet-000001"
  )
  print("\ncreated tweet data index")
except (ConnectionError) as e:
  print(e)

path = os.path.dirname(os.path.abspath(__file__)) + '/mock-tweet-data-es-design.json'
with open(path) as f:
    tweet_data_2 = json.load(f)


try:
# use the helpers library's Bulk API to index list of Elasticsearch docs
  resp = bulk(
  es,
  tweet_data_2,
  index = "tweet-000002"
  )
  print("\ncreated tweet-2 data index")
except (ConnectionError) as e:
  print(e)



class DbPersistanceHandler():

    def __init__(self):
        self.conn_string = "host={} port={} dbname={} user={} password={}".format(
            'postgres', '5432', 'sqlpad','sqlpad', 'sqlpad')
        self.user_table_name = 'user_data'
        self.tweet_table_name = 'tweet_data'
        self.connection = None

    def getConnection(self):
        if self.connection is None:
            self.connection = psycopg2.connect(self.conn_string)
        return self.connection

    def closeConnection(self):
        if self.connection is not None:
            self.connection.close()

    def createTableIfNotExists(self,user_data,tweet_data):
        create_user_table =  "create table if not exists user_data(id int PRIMARY KEY,first_name varchar(64) NOT NULL,last_name varchar(64) NOT NULL,age int NOT NULL,gender varchar(64) NOT NULL,email varchar(64) NOT NULL,created_at timestamp NOT NULL,modified_at timestamp NOT NULL);"

        create_tweet_table = "create table if not exists tweet_data(id int PRIMARY KEY,tweet varchar(512) NOT NULL,user_id int NOT NULL,created_at timestamp NOT NULL,modified_at timestamp NOT NULL, CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES user_data(id));"

        try:
            db_connection = self.getConnection()
            cursor = db_connection.cursor()
            cursor.execute(create_user_table)
            logger.info("executed query to create user table {!r}".
                        format(create_user_table))

            cursor.execute(create_tweet_table)
            logger.info("executed query to create tweet table {!r}".
                        format(create_tweet_table))

            extras.execute_batch(cursor, "INSERT INTO "+self.user_table_name + """ VALUES(
                                     %(id)s,
                                     %(first_name)s,
                                     %(last_name)s,
                                     %(age)s,
                                     %(gender)s,
                                     %(email)s,
                                     %(created_at)s,
                                     %(modified_at)s);""",
                                     user_data)
            logger.info("created {!r} number of compare_metric_aggs".format(
                len(user_data)))


            extras.execute_batch(cursor, "INSERT INTO "+self.tweet_table_name + """ VALUES(
                                     %(id)s,
                                     %(tweet)s,
                                     %(user_id)s,
                                     %(created_at)s,
                                     %(modified_at)s);""",
                                     tweet_data)
            logger.info("upserted {!r} number of compare_metric_aggs".format(
                len(tweet_data)))

            db_connection.commit()
        except (psycopg2.DatabaseError) as error:
            raise error
        finally:
            if cursor is not None:
                cursor.close()

db_persistance_handler =  DbPersistanceHandler()
db_persistance_handler.createTableIfNotExists(user_data,tweet_data_1)

