from hashlib import sha256


def update_hash(*args):
    hashing_text = ""
    h = sha256()
    for arg in args:
        hashing_text += str(arg)
    h.update(hashing_text.encode('utf-8'))
    return h.hexdigest()


class Block:
    def __init__(self, number=0, previous_hash='0'*64, data=None, nonce=0):
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.data = data
        self.number = number

    def hash(self):
        # update the hash value from "0"*64 to sha256 utf-8 encoded cipher text
        return update_hash(self.previous_hash, self.number, self.data, self.nonce)

    def __str__(self):
        # overriding the string method
        return str("Block#: %s\nHash: %s\nPrevious: %s\nData: %s\nNones: %s" % (
            self.number,
            self.hash(),
            self.previous_hash,
            self.data,
            self.nonce
        ))


class Blockchain:
    # Difficulty is number of zeros in the beginning of hash code
    difficulty = 5

    def __init__(self):
        self.chain = []

    def add(self, block):  # creating a chain of blocks i.e. list(blocks)
        self.chain.append(block)

    def remove(self, block):
        self.remove(block)

    def isValid(self):
        # Checking if previous hash is correct and if current hash is same as calculated hash for given data.
        for i in range(1, len(self.chain)):
            _previous = self.chain[i].previous_hash
            _current = self.chain[i - 1].hash()
            if _previous != _current or _current[:self.difficulty] != "0" * self.difficulty:
                return False
        return True

    def mining(self, block):
        try:
            block.previous_hash = self.chain[-1].hash()
        except IndexError:
            pass
        while True:
            if block.hash()[:self.difficulty] == '0' * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1


""" def add(self, block):
    self.chain.append(
        {
            'Hash': block.hash(),
            'previous': block.previous_hash,
            'data': block.data,
            'Block#': block.number,
            'nones': block.nonce
        })"""


def main():
    blockchain = Blockchain()
    database = ["Hellow", "Penguin", "How_r_u?", "bye"]
    num = 0
    for data in database:
        num += 1
        blockchain.mining(Block(data, num))

    for block in blockchain.chain:
        print(block)
        print()

    print("Is blockchain valid? ", blockchain.isValid())


if __name__ == "__main__":
    main()
