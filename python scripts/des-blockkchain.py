import heapq
import hashlib
import random
import psycopg2
from psycopg2 import Error
from event import *
from numpy import random as r
TXN_NUM = 1000
txn_interarrival =1

blockchain_name="blk"  # Change Blockchain Name here
tx_per_blk=10
user_num =20

def user_generator(user_num):
    user_list = []
    for i in range(user_num):
        num = random.randint(1,user_num)
        user = hashlib.md5(str(num).encode()).hexdigest()
        user_list.append(user)
    return user_list



def create_trans(timestamp, sender, receiver, amount):
    cursor.execute(f"INSERT INTO {blockchain_name} (id,sender,receiver,ts,amount) VALUES (DEFAULT,'{sender}','{receiver}','{str(timestamp)}',{amount});")

def create_block(timestamp):
    cursor.execute(f"select create_block('{blockchain_name}',{int(timestamp)});")

def random_txn_generator(user_list):
    timestamp = 0
    for i in range(TXN_NUM):
        timestamp += r.exponential(scale=txn_interarrival, size=None)
        sender, receiver = random.sample(user_list, 2)
        amount = random.randint(1,100)
        event = Event(timestamp, [create_trans, timestamp, sender, receiver, amount])
        heapq.heappush(q, event)
    blk_num = TXN_NUM // tx_per_blk
    for i in range(blk_num):
        ts = random.randint(1, int(timestamp))
        event = Event(ts,[create_block,timestamp])
        heapq.heappush(q, event)



connection = psycopg2.connect(user="tula",
                              password="",
                              host="127.0.0.1",
                              port="9432",
                              database="test")
# Create a cursor to perform database operations
cursor = connection.cursor()
# Print PostgreSQL details
print("PostgreSQL server information")
print(connection.get_dsn_parameters(), "\n")
cursor.execute("create extension IF NOT EXISTS blockchain2;")
cursor.execute(f"select init_blockchain2('{blockchain_name}');")
q = []
heapq.heapify(q)
user_list=user_generator(user_num)
random_txn_generator(user_list)

while q:
    obj = heapq.heappop(q)
    t = obj.timestamp
    obj = obj.args
    args = obj[1:]
    func=obj[0]
    print(obj)
    func(*args)
connection.commit()
cursor.execute(f"select * from {blockchain_name}_block;")
results = cursor.fetchall()
for i in results:
    print("")




cursor.close()
connection.close()

