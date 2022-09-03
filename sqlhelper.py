from app import mysql, session
from BlockChain import Block, Blockchain


class InvalidAmountException(Exception):
    def __init__(self, exception='Invalid Amount Entered!!'):
        pass


class InsufficientAmountException(Exception):
    def __init__(self, exception='Insufficient Amount for transaction!!'):
        pass


class InvalidTransactionException(Exception):
    def __init__(self, exception='Invalid Transaction!!!'):
        pass


class Table:
    def __init__(self, table_name, *args):
        self.table_name = table_name
        self.column = "(%s)" % ",".join(args)
        self.column_list = args

        if isNewTable(table_name):
            create_data = ""
            for column in self.column_list:
                create_data += "%s varchar(100)," % column

            cur = mysql.connection.cursor()
            cur.execute("CREATE TABLE %s(%s)" % (self.table_name, create_data[:len(create_data) - 1]))
            cur.close()

    def get_all(self):
        cur = mysql.connection.cursor()
        cur.execute("select * from %s" % self.table_name)
        data = cur.fetchall()
        cur.close()
        return data

    def get_val(self, search, value):
        data = {}
        cur = mysql.connection.cursor()
        result = cur.execute("select * from %s WHERE %s = \"%s\"" % (self.table_name, search, value))
        if result > 0:
            data = cur.fetchone()
        cur.close()
        return data

    def del_val(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("Delete * from %s WHERE %s = \"%s\"" % (self.table_name, search, value))
        mysql.connection.commit()
        cur.close()

    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("Drop Table %s" % self.table_name)
        mysql.connection.commit()
        cur.close()
        self.__init__(self.table_name, *self.column_list)

    def del_All(self):
        self.drop()
        self.__init__(self.table_name, *self.column_list)

    def insert_in(self, *args):
        data = ""
        for arg in args:
            data += "\"%s\"," % arg
        cur = mysql.connection.cursor()
        cur.execute("Insert into %s%s values(%s)" % (self.table_name, self.column, data[:len(data) - 1]))
        mysql.connection.commit()
        cur.close()


def isNewTable(tableName):
    cur = mysql.connection.cursor()
    try:
        res = cur.execute("select * from %s" % tableName)
        cur.close()
    except:
        return True
    else:
        return False


def sqlRaw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()


def isNewUser(username):
    users = Table("users", "name", "email", "username", "password")
    data = users.get_all()
    usernames = [users.get('username') for users in data]
    # print(usernames)
    return False if username in usernames else True


def send_money(sender, recipient, amount):
    try:
        amount = float(amount)
    except ValueError:
        raise InvalidAmountException('Invalid Amount Entered.')

    if amount > get_balance(sender) and sender != 'Bank':
        raise InsufficientAmountException('Insufficient transaction amount.')
    elif sender == recipient or amount <= 0.00:
        raise InvalidTransactionException('Transaction Invalid!!!')
    elif isNewUser(recipient):
        raise InvalidTransactionException("Any of user doesn't exist...")

    blockchain = get_blockchain()
    number = len(blockchain.chain) + 1
    data = "%s-->%s-->%s" % (sender, recipient, amount)
    blockchain.mining(Block(data=data, number=number))
    sync_blockchain(blockchain)


def get_balance(username):
    balance = 0.00
    blockchain = get_blockchain()
    for block in blockchain.chain:
        data = block.data.split('-->')
        if username == data[0]:
            balance -= float(data[2])
        elif username == data[1]:
            balance += float(data[2])
    return balance


def get_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table("blockchain", 'number', 'hash', 'previous', 'data', 'nonce')
    for b in blockchain_sql.get_all():
        blockchain.add(Block(int(b.get('number')), b.get('previous'), b.get('data'), b.get('nonce')))
    return blockchain


def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", 'number', 'hash', 'previous', 'data', 'nonce')
    blockchain_sql.del_All()
    for block in blockchain.chain:
        blockchain_sql.insert_in(str(block.number), block.hash(), block.previous_hash, block.data, block.nonce)




def test_blockchain():
    blockchain_sql = Table("blockchain", 'number', 'hash', 'previous', 'data', 'nonce')
    blockchain_sql.del_All()
    """database = ["Hellow", "Penguin", "How_r_u?", "bye"]
    num = 0
    for data in database:
        num += 1
        blockchain.mining(Block(data=data, number=num))
    for block in blockchain.chain:
        print(block)
        print()
    print("Is blockchain valid? ", blockchain.isValid())
    sync_blockchain(blockchain)"""
