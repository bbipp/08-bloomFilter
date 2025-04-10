import math
import mmh3
import random
import threading

x = 1
y = x.to_bytes(math.ceil(x.bit_length() / 8), "big")
print (mmh3.mmh3_32_uintdigest(y, 2538058380))

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

thread_local_random = ThreadLocalRandom()

class BloomFilter:
    # defaults to making bloom filter with 1% false positive rate
    def __init__(self, n, P=0.01, m=None):
        if m is None:
            self.m = self.get_m_by_p(P, n) # makes bloomFilter size depending on P and n
        else:
            self.m = m # creates a bloomFilter of size m
        self.n = n
        self.bit = [None] * self.m
        self.k = self.optimal_k(self.m, self.n)
        self.set_seeds(self.k)

    # sets m to guarantee a probability P on n inputs
    def get_m_by_p(P, n):
        return int(-(n * Math.log(P)) / Math.pow(Math.log(2), 2))

    # returns optimal number of hashing functions given n and m
    def optimal_k(self, m, n):
        return int((m / n) * math.log(2))

    def set_seeds(self, k):
        self.k = k
        self.seeds = [thread_local_random.next_long() for _ in range(k)]
