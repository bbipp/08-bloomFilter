import math
import mmh3
import random
import threading
import struct

# x = 1
# y = x.to_bytes(math.ceil(x.bit_length() / 8), "big")
# print (mmh3.mmh3_32_uintdigest(y, 2538058380))

class ThreadLocalRandom:
    def __init__(self):
        self.local = threading.local()

    def get_random(self):
        if not hasattr(self.local, 'random'):
            self.local.random = random.Random()
        return self.local.random

    def seed(self, a=None):
        self.get_random().seed(a)

    def next_long(self):
        return self.get_random().getrandbits(64)

class BloomFilter:
    # defaults to making bloom filter with 1% false positive rate
    def __init__(self, n, P=0.01, m=None):
        self.thread_local_random = ThreadLocalRandom()
        if m is None:
            self.m = self.get_m_by_p(P, n) # makes bloomFilter size depending on P and n
        else:
            self.m = m # creates a bloomFilter of size m
        self.n = n
        self.bit = [False] * self.m
        self.k = self.optimal_k(self.m, self.n)
        self.set_seeds(self.k)

    def set_m(self, m):
        self.m = m

    def set_n(self, n):
        self.n = n
        
    # sets m to guarantee a probability P on n inputs
    def get_m_by_p(self, P, n):
        return int(-(n * math.log(P)) / math.pow(math.log(2), 2))

    # returns optimal number of hashing functions given n and m
    def optimal_k(self, m, n):
        return int((m / n) * math.log(2))

    def set_seeds(self, k):
        self.k = k
        rng = random.Random()  # Create a separate RNG instance
        self.seeds = [rng.randint(0, 2147483647) for _ in range(k)]
        #self.seeds = [rng.getrandbits(64) for _ in range(k)]
        # self.seeds = [self.thread_local_random.next_long() for _ in range(k)]

    def add_string(self, s):
        for i in range(self.k):
            h = self.hash_string(s, self.seeds[i])
            self.bit[h % self.m] = True

    # wrapper for string hashing -- in python3 long is also included in int
    def hash_string(self, s, seed):
        # Convert string to bytes
        byte_array = s.encode('utf-8')
        # Call Murmur3 hash function
        return mmh3.hash(byte_array, seed) & 0xffffffff

    def add_int(self, n):
        for i in range(self.k):
            h = self.hash_int(n, self.seeds[i])
            self.bit[h % self.m] = True

    def hash_int(self, n, seed):
        # Convert string to bytes
        big_int_n = int(n)
        byte_array = self.to_byte_array(big_int_n)
        # byte_array = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big') or b'\0'
        return mmh3.hash(byte_array, seed) & 0xffffffff

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

    def contains(self, s):
        for i in range(self.k):
            h = self.hash_string(s, self.seeds[i])  # use string hash here
            if not self.bit[h % self.m]:
                return False
        return True

def main():
    num_inputs, num_checks = map(int, input().split())
    bf = BloomFilter(num_inputs)

    for _ in range(num_inputs):
        s = input().strip()
        bf.add_string(s)

    in_ = 0

    for _ in range(num_checks):
        s = input().strip()
        if bf.contains(s):
            in_ += 1

    print(f"In: {in_}")
    print(f"Out: {num_checks - in_}")

if __name__ == "__main__":
    main()