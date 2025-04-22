import math
import random

IPMASK = 0xffffffff

class BloomFilter:
    def __init__(self, n, m=None, P=0.01, col=None):
        self.n = n
        if col is not None:
            self.m = sel.getMByP(0.01, n)
            self.collisions = [False] * self.m
        if P is not None:
            self.m = self.getMByP(0.01, n)
        if m is not None:
            self.m = m
        self.bit = [False] * self.m
        self.k = self.optimal_k(self.m, n)
        self.set_seeds(self.k)

    def set_seeds(self, k):
        self.k = k
        rng = random.Random()  # Create a separate RNG instance
        self.seeds = [rng.getrandbits(64) for _ in range(k)]

    # sets m to guarantee a probability P on n inputs
    def get_m_by_p(self, P, n):
        return int(-(n * math.log(P)) / math.pow(math.log(2), 2))

    def set_m(self, m):
        self.m = m

    def set_n(self, n):
        self.n = n

    # returns optimal number of hashing functions given n and m
    def optimal_k(self, m, n):
        return int((m / n) * math.log(2))
    
    def add_string(self, s):
        for i in range(self.k):
            h = self.hash_string(s, self.seeds[i])
            self.bit[h % self.m] = True

    # wrapper for string hashing -- in python3 long is also included in int
    def hash_string(self, s, seed):
        # Convert string to bytes
        byte_array = s.encode('utf-8')
        # Call Murmur3 hash function
        return mmh3.hash(bytes(byte_array), len(s), seed)

    # https://stackoverflow.com/questions/23870859/tobytearray-in-python
    def to_byte_array(self, num):
        bytea = []
        n = num
        while n:
            bytea.append(n % 256)
            n //= 256
        n_bytes = len(bytea)
        if 2 ** (n_bytes * 8 - 1) <= num < 2 ** (n_bytes * 8):
            bytea.append(0)
        return bytearray(reversed(bytea))

    # for STRING only....if need contains for an int will need to change
    def contains(self, s):
        for i in range(self.k):
            h = self.hash_string(s, self.seeds[i])  # use string hash here
            if not self.bit[h % self.m]:
                return False
        return True

    # method to add an int that can be deleted
    def add_collision(self, n):
    for i in range(self.k):
        s = self.seeds[i]
        h = self.hash_string(n, s)
        if self.bit[h % self.m] is True:
            self.collisions[h % self.m] = True

    def delete(self, n):
    for i in range(self.k):
        s = self.seeds[i]
        h = self.hash_string(n, s)
        if self.collisions[h % self.m] is False:
            self.bit[h % self.m] = False

    