import math
import mmh3
import random
import threading
import struct

class BloomFilter:
    # defaults to making bloom filter with 1% false positive rate
    def __init__(self, n, P=0.01, m=None):
        """
        n: Expected number of elements.
        m: Size of bit array. If None, computed from false positive
           probability P using m = -(n * ln(P)) / (ln2)^2.
        P: Target false positive probability.
        bit: Bloom Filter array representation
        k: Number of hash functions
        """
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

    # sets k seed values to random numbers
    def set_seeds(self, k):
        self.k = k
        rng = random.Random()
        self.seeds = [rng.randint(0, 2147483647) for _ in range(k)]

    # insertion for a string
    def add_string(self, s):
        for i in range(self.k): # go through all the hash functions
            h = self.hash_string(s, self.seeds[i]) # get the index from the current hash function
            self.bit[h % self.m] = True # change the corresponding bit in the bit array to be True

    # wrapper for string hashing
    def hash_string(self, s, seed):
        byte_array = s.encode('utf-8') # Convert string to bytes
        return mmh3.hash(byte_array, seed) & 0xffffffff # call mmh3 hash function and then do a bit shift to ensure non-negative

    # insertion for a string
    def add_int(self, n):
        for i in range(self.k):
            h = self.hash_int(n, self.seeds[i])
            self.bit[h % self.m] = True

    # wrapper for int hashing
    def hash_int(self, n, seed):
        big_int_n = int(n)
        byte_array = self.to_byte_array(big_int_n) # convert to bytes
        return mmh3.hash(byte_array, seed) & 0xffffffff # call mmh3 hash function and then do a bit shift to ensure non-negative

    # convert an int to a byte array
    def to_byte_array(self, num): # https://stackoverflow.com/questions/23870859/tobytearray-in-python
        bytea = []
        n = num
        while n:
            bytea.append(n % 256)
            n //= 256
        n_bytes = len(bytea)
        if 2 ** (n_bytes * 8 - 1) <= num < 2 ** (n_bytes * 8):
            bytea.append(0)
        return bytearray(reversed(bytea))

    # query element membership in Bloom Filter
    def contains(self, s):
        for i in range(self.k): # go through k hash filters
            h = self.hash_string(s, self.seeds[i])  # get index by hashing element for current hash "seed"
            if not self.bit[h % self.m]:
                return False
        return True # element only in filter if every index mapped by the hashing functions has been set to True

def main():
    num_inputs, num_checks = map(int, input().split())
    bf = BloomFilter(num_inputs)

    # input
    for _ in range(num_inputs):
        s = input().strip()
        bf.add_string(s)

    in_ = 0

    # output
    for _ in range(num_checks):
        s = input().strip()
        if bf.contains(s):
            in_ += 1

    print(f"In: {in_}")
    print(f"Out: {num_checks - in_}")

if __name__ == "__main__":
    main()