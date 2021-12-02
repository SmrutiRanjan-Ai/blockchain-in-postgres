import psycopg2
from psycopg2 import Error
import os
import datetime
import hashlib
dirA = '/home/tula/Documents/631/blockchain/'  # Directory where blk*.dat files are stored
def merkle_root(lst): # https://gist.github.com/anonymous/7eb080a67398f648c1709e41890f8c44
    sha256d = lambda x: hashlib.sha256(hashlib.sha256(x).digest()).digest()
    hash_pair = lambda x, y: sha256d(x[::-1] + y[::-1])[::-1]
    if len(lst) == 1: return lst[0]
    if len(lst) % 2 == 1:
        lst.append(lst[-1])
    return merkle_root([hash_pair(x,y) for x, y in zip(*[iter(lst)]*2)])
    
def read_bytes(file,n,byte_order = 'L'):
    data = file.read(n)
    if byte_order == 'L':
        data = data[::-1]
    data = data.hex().upper()
    return data

def read_varint(file):
    b = file.read(1)
    bInt = int(b.hex(),16)
    c = 0
    data = ''
    if bInt < 253:
        c = 1
        data = b.hex().upper()
    if bInt == 253: c = 3
    if bInt == 254: c = 5
    if bInt == 255: c = 9
    for j in range(1,c):
        b = file.read(1)
        b = b.hex().upper()
        data = b + data
    return data
def reverse(input):
    L = len(input)
    if (L % 2) != 0:
        return None
    else:
        Res = ''
        L = L // 2
        for i in range(L):
            T = input[i*2] + input[i*2+1]
            Res = T + Res
            T = ''
        return (Res);
try:
    # Connect to an existing database

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
    # Executing a SQL query
    i=0
    cursor.execute("CREATE TABLE IF NOT EXISTS BITCOIN_BLOCKS ( id serial, prev_hash text not null, block_hash text not null, nonce text not null, merkle_root text not null, difficulty text not null, timestamp text not null, tx_count int not null,  version text not null, block_size text not null);")
    cursor.execute("create index bitcoin_index on BITCOIN_BLOCKS using lsm3(id);")
    cursor.execute("CREATE TABLE IF NOT EXISTS BITCOIN_TX ( id serial, input_hash text not null, input_script text not null, input_num int not null, output_script text not null, output_num int not null, tx_hash text not null, block_hash text not null, value text not null);")
    connection.commit()


    fList = os.listdir(dirA)
    fList = [x for x in fList if (x.endswith('.dat') and x.startswith('blk'))]
    fList.sort()

    for i in fList:
        nameSrc = i
        nameRes = nameSrc.replace('.dat', '.txt')
        resList = []
        a = 0
        t = dirA + nameSrc
        resList.append('Start ' + t + ' in ' + str(datetime.datetime.now()))
        print('Start ' + t + ' in ' + str(datetime.datetime.now()))
        f = open(t, 'rb')
        tmpHex = ''
        fSize = os.path.getsize(t)
        while f.tell() != fSize:
            tmpHex = read_bytes(f, 4)
            blocksize = read_bytes(f, 4)
            tmpPos3 = f.tell()
            tmpHex = read_bytes(f, 80, 'B')
            tmpHex = bytes.fromhex(tmpHex)
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = tmpHex[::-1]
            tmpHex = tmpHex.hex().upper()
            blockhash=tmpHex
            f.seek(tmpPos3, 0)
            tmpHex = read_bytes(f, 4)
            version=tmpHex
            tmpHex = read_bytes(f, 32)
            prevhash=tmpHex
            tmpHex = read_bytes(f, 32)
            merkleroot = tmpHex
            tmpHex = read_bytes(f, 4)
            timestamp=tmpHex
            tmpHex = read_bytes(f, 4)
            difficulty = tmpHex
            tmpHex = read_bytes(f, 4)
            nonce=tmpHex
            tmpHex = read_varint(f)
            txCount = int(tmpHex, 16)
            tx_num=txCount
            tmpHex = '';
            RawTX = '';
            tx_hashes = []
            cursor.execute(f"INSERT INTO BITCOIN_BLOCKS VALUES (DEFAULT,'{prevhash}','{blockhash}','{nonce}','{merkleroot}','{difficulty}','{timestamp}','{tx_num}','{version}','{blocksize}');")
            print(f"Block {blockhash} Added")
            for k in range(txCount):
                tmpHex = read_bytes(f, 4)
                RawTX = reverse(tmpHex)
                tmpHex = ''
                Witness = False
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                if bInt == 0:
                    tmpB = ''
                    f.seek(1, 1)
                    c = 0
                    c = f.read(1)
                    bInt = int(c.hex(), 16)
                    tmpB = c.hex().upper()
                    Witness = True
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = hex(bInt)[2:].upper().zfill(2)
                    tmpB = ''
                if bInt == 253: c = 3
                if bInt == 254: c = 5
                if bInt == 255: c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                inCount = int(tmpHex, 16)
                inputnum=inCount
                tmpHex = tmpHex + tmpB
                RawTX = RawTX + reverse(tmpHex)
                inputscript=''
                inputhash=''
                for m in range(inCount):
                    tmpHex = read_bytes(f, 32)
                    inputhash = tmpHex
                    RawTX = RawTX + reverse(tmpHex)
                    tmpHex = read_bytes(f, 4)
                    RawTX = RawTX + reverse(tmpHex)
                    tmpHex = ''
                    b = f.read(1)
                    tmpB = b.hex().upper()
                    bInt = int(b.hex(), 16)
                    c = 0
                    if bInt < 253:
                        c = 1
                        tmpHex = b.hex().upper()
                        tmpB = ''
                    if bInt == 253: c = 3
                    if bInt == 254: c = 5
                    if bInt == 255: c = 9
                    for j in range(1, c):
                        b = f.read(1)
                        b = b.hex().upper()
                        tmpHex = b + tmpHex
                    scriptLength = int(tmpHex, 16)
                    tmpHex = tmpHex + tmpB
                    RawTX = RawTX + reverse(tmpHex)
                    tmpHex = read_bytes(f, scriptLength, 'B')
                    inputscript = tmpHex
                    RawTX = RawTX + tmpHex
                    tmpHex = read_bytes(f, 4, 'B')
                    RawTX = RawTX + tmpHex
                    tmpHex = ''
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = b.hex().upper()
                    tmpB = ''
                if bInt == 253: c = 3
                if bInt == 254: c = 5
                if bInt == 255: c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                outputCount = int(tmpHex, 16)
                tmpHex = tmpHex + tmpB
                outputnum=outputCount
                RawTX = RawTX + reverse(tmpHex)
                outputscript=''
                Value=''
                for m in range(outputCount):
                    tmpHex = read_bytes(f, 8)
                    Value=tmpHex
                    RawTX = RawTX + reverse(tmpHex)
                    tmpHex = ''
                    b = f.read(1)
                    tmpB = b.hex().upper()
                    bInt = int(b.hex(), 16)
                    c = 0
                    if bInt < 253:
                        c = 1
                        tmpHex = b.hex().upper()
                        tmpB = ''
                    if bInt == 253: c = 3
                    if bInt == 254: c = 5
                    if bInt == 255: c = 9
                    for j in range(1, c):
                        b = f.read(1)
                        b = b.hex().upper()
                        tmpHex = b + tmpHex
                    scriptLength = int(tmpHex, 16)
                    tmpHex = tmpHex + tmpB
                    RawTX = RawTX + reverse(tmpHex)
                    tmpHex = read_bytes(f, scriptLength, 'B')
                    outputscript = tmpHex
                    RawTX = RawTX + tmpHex
                    tmpHex = ''
                if Witness == True:
                    for m in range(inCount):
                        tmpHex = read_varint(f)
                        WitnessLength = int(tmpHex, 16)
                        for j in range(WitnessLength):
                            tmpHex = read_varint(f)
                            WitnessItemLength = int(tmpHex, 16)
                            tmpHex = read_bytes(f, WitnessItemLength)
                            tmpHex = ''
                Witness = False
                tmpHex = read_bytes(f, 4)
                RawTX = RawTX + reverse(tmpHex)
                tmpHex = RawTX
                tmpHex = bytes.fromhex(tmpHex)
                tmpHex = hashlib.new('sha256', tmpHex).digest()
                tmpHex = hashlib.new('sha256', tmpHex).digest()
                tmpHex = tmpHex[::-1]
                tmpHex = tmpHex.hex().upper()
                txhash=tmpHex
                tx_hashes.append(tmpHex)
                tmpHex = '';
                RawTX = ''
                cursor.execute(f"INSERT INTO BITCOIN_TX VALUES (DEFAULT,'{inputhash}','{inputscript}',{inputnum},'{outputscript}',{outputnum},'{txhash}','{blockhash}','{Value}');")
            a += 1
            tx_hashes = [bytes.fromhex(h) for h in tx_hashes]
            tmpHex = merkle_root(tx_hashes).hex().upper()
            if tmpHex != merkleroot:
                print('Merkle roots does not match! >', merkleroot, tmpHex)

    cursor.execute(f"select * from BITCOIN_BLOCKS;")
    results = cursor.fetchmany(5)
    print("Block List")
    for i in results:
        print(i)

    connection.commit()
except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

