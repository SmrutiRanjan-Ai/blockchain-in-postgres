\echo Use "CREATE EXTENSION blockchain2" to load this file. \quit
CREATE OR REPLACE FUNCTION init_blockchain2(t_name varchar(30))
  RETURNS VOID
AS $block$
  plpy.execute(f"""CREATE TABLE IF NOT EXISTS {t_name} (
       id serial PRIMARY KEY,
       sender varchar(66) NOT NULL,
       receiver varchar(66) NOT NULL,
       ts text NOT NULL, 
       amount INT NOT NULL,
       blockhash varchar(66))""")
  plpy.execute(f"""CREATE TABLE IF NOT EXISTS {t_name}_block (
       id serial PRIMARY KEY,
       prevhash varchar(66) NOT NULL,
       nonce int NOT NULL,
       ts int NOT NULL, 
       merklehash text NOT NULL,
       difficulty text NOT NULL,
       blockhash text NOT NULL)""")
      
$block$ LANGUAGE plpython3u;



CREATE OR REPLACE FUNCTION create_block(t_name text, ts integer)
  RETURNS VOID
AS $powblock$
  import hashlib
  import random
  import time
  import math
  THRESHOLD="0000"
  
  def add_mkl_tree(trans_list):
        '''create merkle tree from list of transactions or data . The merkle tree here is slightly different than in bitcoin
         Here blank leaf nodes are nt replaced with duplicate tx. Its given None Value
         '''
        
        ln = len(trans_list)
        level = int(math.log2(ln))
        n=2 ** (level)
        if n<ln:
          n=n*4 -1
        else:
          n=n*2-1
        mkl_list = [None for _ in range(n)]
        for i in range(ln):
          plpy.log(n,level,ln,i,ln - 1 + i)
          mkl_list[ln - 1 + i] = hashlib.sha256(str(trans_list[i]).encode()).hexdigest()
            

        while level > 0:
            for k in range(0, 2 ** level, 2):
                index = 2 ** level - 1
                parent = (index + k) // 2
                hash_str = str(mkl_list[index + k]) + str(mkl_list[index + k + 1])
                mkl_list[parent] = hashlib.sha256(hash_str.encode()).hexdigest()
            level -= 1
        return mkl_list[0]
  

  def proof_of_work(block_table_name,prev_hash,mkl_root,threshold,ts):
    '''calculate proof of work of a temp block'''
    nonce = random.randint(2, 100)
    adder = random.randint(2, 100)
    n = len(threshold)
    while True:
        hash_str = prev_hash + mkl_root + str(nonce) + str(ts) + threshold
        pow_hash = hashlib.sha256(hash_str.encode()).hexdigest()
        if pow_hash[:n] == threshold:
            break
        else:
            nonce = nonce + adder
    plpy.execute(f"""INSERT INTO {block_table_name} VALUES (DEFAULT,'{prev_hash}',{nonce},{ts},'{mkl_root}','{threshold}','{pow_hash}')""")
    return pow_hash
    
  '''Main Function Starts Here'''
  block_table_name=t_name+"_block"
  rows=plpy.execute(f"""SELECT * from {t_name} where blockhash IS NULL""")
  hash_list=[]
  for row in rows:
    s=""
    for key in row:
      if key=="blockhash":
        continue
      s+=str(row[key])
    hash_list.append(hashlib.sha256(s.encode()).hexdigest())
  plpy.log(len(hash_list))
  if hash_list:
    mkl_root=add_mkl_tree(hash_list)
  else:
    return
  '''get prev hash from last row of blocks table'''
  last=plpy.execute(f"select * from {t_name}_block ORDER BY id DESC ",1)
  if last:
    prev_hash=last[0]['blockhash']

  else:
    prev_hash="0"
    
  block_hash=proof_of_work(block_table_name,prev_hash,mkl_root,THRESHOLD,ts)
  plpy.execute(f"UPDATE {t_name} SET blockhash='{block_hash}' where blockhash IS NULL")
  
    
$powblock$ LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION check_integrity(t_name varchar(30))
  RETURNS text
AS $block$
  import hashlib
  import random
  import math
  def check_pow(prev_hash,mkl_root,nonce,ts,threshold,block_hash):
    '''check proof of work of old block'''
    hash_str = prev_hash + mkl_root + str(nonce) + str(ts) + threshold
    if block_hash == hashlib.sha256(hash_str.encode()).hexdigest():
        return True
    else:
        return False
  def check_mkl_tree(trans_list,merkle_root):
        '''check intgegrity of merkle tree'''
        
        ln = len(trans_list)
        level = int(math.log2(ln))
        n=2 ** (level)
        if n<ln:
          n=n*4 -1
        else:
          n=n*2-1
        mkl_list = [None for _ in range(n)]
        for i in range(ln):
            mkl_list[ln - 1 + i] = hashlib.sha256(str(trans_list[i]).encode()).hexdigest()

        while level > 0:
            for k in range(0, 2 ** level, 2):
                index = 2 ** level - 1
                parent = (index + k) // 2
                hash_str = str(mkl_list[index + k]) + str(mkl_list[index + k + 1])
                mkl_list[parent] = hashlib.sha256(hash_str.encode()).hexdigest()
            level -= 1
        
        if mkl_list[0]==merkle_root:
          return True
        else:
          return False
  blocks=plpy.execute(f"select * from {t_name}_block")
  prev_hash="0"
  for block in blocks:
    if block['prevhash']==prev_hash:
      block_hash=block['blockhash']
      mkl_root=block['merklehash']
      threshold=block['difficulty']
      nonce=block['nonce']
      ts=block['ts']
      rows=plpy.execute(f"select * from {t_name} where blockhash='{block_hash}'")
      hash_list=[]
      for row in rows:
        s=""
        for key in row:
          if key=="blockhash":
            continue
          s+=str(row[key])
        hash_list.append(hashlib.sha256(s.encode()).hexdigest())
      is_mkl=check_mkl_tree(hash_list,block['merklehash'])
      is_pow=check_pow(prev_hash,mkl_root,nonce,ts,threshold,block_hash)
      if is_mkl and is_pow:
        prev_hash=block_hash
        continue
      else:
        return False
  return True
      
    
       
      
$block$ LANGUAGE plpython3u;



