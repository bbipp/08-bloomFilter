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
        self.bit = [None] * self.m
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
        self.seeds = [self.thread_local_random.next_long() for _ in range(k)]

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

    def add_int(self, n):
        for i in range(self.k):
            h = self.hash_int(n, self.seeds[i])
            self.bit[h % self.m] = True

    def hash_int(self, n, seed):
        # Convert string to bytes
        big_int_n = int(n)
        byte_array = self.to_byte_array(big_int_n)
        # byte_array = n.to_bytes((n.bit_length() + 7) // 8, byteorder='big') or b'\0'
        return mmh3.hash(bytes(byte_array), len(byte_array), seed)

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
            h = self.hash_int(s, self.seeds[i])
            if not self.bit[h % self.m]:  # Check if the bit is False
                return False
        return True

class Murmur3:
    UNSIGNED_MASK = 0xff
    UINT_MASK = 0xFFFFFFFF
    LONG_MASK = 0xFFFFFFFFFFFFFFFF

    X86_32_C1 = 0xcc9e2d51
    X86_32_C2 = 0x1b873593
    X64_128_C1 = 0x87c37b91114253d5
    X64_128_C2 = 0x4cf5ad432745937f

    @staticmethod
    def hash_x86_32(data: bytes, length: int, seed: int) -> int:
        nblocks = length >> 2
        _hash = seed

        # body
        for i in range(nblocks):
            i4 = i << 2
            k1 = (data[i4] & Murmur3.UNSIGNED_MASK)
            k1 |= (data[i4 + 1] & Murmur3.UNSIGNED_MASK) << 8
            k1 |= (data[i4 + 2] & Murmur3.UNSIGNED_MASK) << 16
            k1 |= (data[i4 + 3] & Murmur3.UNSIGNED_MASK) << 24
            
            k1 = (k1 * Murmur3.X86_32_C1) & Murmur3.UINT_MASK
            k1 = Murmur3.rotl32(k1, 15)
            k1 = (k1 * Murmur3.X86_32_C2) & Murmur3.UINT_MASK

            hash_ ^= k1
            hash_ = Murmur3.rotl32(hash_, 13)
            hash_ = (((hash_ * 5) & Murmur3.UINT_MASK) + 0xe6546b64) & Murmur3.UINT_MASK

        # tail
        offset = nblocks << 2
        k1 = 0

        # advance offset to the unprocessed tail of the data.
        tail_size = length & 3
        if tail_size == 3:
            k1 ^= (data[offset + 2] << 16) & Murmur3.UINT_MASK
        if tail_size == 2:
            k1 ^= (data[offset + 1] << 8) & Murmur3.UINT_MASK
        if tail_size == 1:
            k1 ^= data[offset]
            k1 = (k1 * Murmur3.X86_32_C1) & Murmur3.UINT_MASK
            k1 = Murmur3.rotl32(k1, 15)
            k1 = (k1 * Murmur3.X86_32_C2) & Murmur3.UINT_MASK
            hash_ ^= k1

        # finalization
        hash_ ^= length
        hash_ = Murmur3.fmix32(hash_)

        return hash_

    @staticmethod
    def hash_x64_128(data: bytes, length: int, seed: int) -> tuple:
        h1 = seed
        h2 = seed
        
        buffer = io.BytesIO(data)
        def remaining():
            return len(data) - buffer.tell()

        while remaining() >= 16:
            k1_bytes = buffer.read(4) # MAY BE INCORRECT...basing this off a long being four bytes
            k2_bytes = buffer.read(4) # MAY BE INCORRECT...basing this off a long being four bytes

            # apply endianness
            k1 = struct.unpack('<q', k1_bytes)[0]
            k2 = struct.unpack('<q', k2_bytes)[0]

            h1 ^= Murmur3.mixK1(k1)
            h1 = Murmur3.rotate_left(h1, 27)
            h1 += h2
            h1 = h2 * 5 + 0x52dce729

            h2 ^= Murmur3.mixK2(k2)
            h2 = Murmur3.rotate_left(h2, 31)
            h2 += h1
            h2 = h2 * 5 + 0x38495ab5

        tail = data[-remaining():]

        # Tail
        k1 = 0
        k2 = 0
        tail_len = len(tail)

        if tail_len > 0:
            if tail_len >= 15: k2 ^= (tail[14] & Murmur3.UNSIGNED_MASK) << 48
            if tail_len >= 14: k2 ^= (tail[13] & Murmur3.UNSIGNED_MASK) << 40
            if tail_len >= 13: k2 ^= (tail[12] & Murmur3.UNSIGNED_MASK) << 32
            if tail_len >= 12: k2 ^= (tail[11] & Murmur3.UNSIGNED_MASK) << 24
            if tail_len >= 11: k2 ^= (tail[10] & Murmur3.UNSIGNED_MASK) << 16
            if tail_len >= 10: k2 ^= (tail[9] & Murmur3.UNSIGNED_MASK) << 8
            if tail_len >= 9:  k2 ^= (tail[8] & Murmur3.UNSIGNED_MASK)

            if tail_len >= 8:
                k1 ^= struct.unpack_from('<Q', tail[:8])[0]
            else:
                if tail_len >= 7: k1 ^= (tail[6] & Murmur3.UNSIGNED_MASK) << 48
                if tail_len >= 6: k1 ^= (tail[5] & Murmur3.UNSIGNED_MASK) << 40
                if tail_len >= 5: k1 ^= (tail[4] & Murmur3.UNSIGNED_MASK) << 32
                if tail_len >= 4: k1 ^= (tail[3] & Murmur3.UNSIGNED_MASK) << 24
                if tail_len >= 3: k1 ^= (tail[2] & Murmur3.UNSIGNED_MASK) << 16
                if tail_len >= 2: k1 ^= (tail[1] & Murmur3.UNSIGNED_MASK) << 8
                if tail_len >= 1: k1 ^= (tail[0] & Murmur3.UNSIGNED_MASK)

            h1 ^= Murmur3.mixK1(k1)
            h2 ^= Murmur3.mixK2(k2)

        # Finalization
        h1 ^= length
        h2 ^= length

        h1 = h1 + h2
        h2 = h2 + h1

        h1 = Murmur3.fmix64(h1)
        h2 = Murmur3.fmix64(h2)

        h1 = h1 + h2
        h2 = h2 + h1

        return (h1, h2)

    @staticmethod
    def get_long(buffer):
        # Read 8 bytes and unpack them as little-endian signed long (q format)
        long_value = struct.unpack('<q', buffer.read(8))[0]  # < for little-endian, q for long
        return long_value

    @staticmethod
    def rotate_left(n, d, bit_size=32): # 32 is standard for int in python I believe
        d %= bit_size
        return ((n << d) | (n >> (bit_size - d))) & ((1 << bit_size) - 1) # mask to ensure it fits within bit_size to turn left like the built in long method in java
     
    @staticmethod
    def mixK1(k1):
        k1 *= Murmur3.X64_128_C1
        k1 = rotate_left(k1, 31)
        k1 *= Murmur3.X64_128_C2
        return k1

    @staticmethod
    def mixK2(k2):
        k2 *= Murmur3.X64_128_C2
        k2 = rotate_left(k2, 33)
        k2 *= Murmur3.X64_128_C1
        return k2

    @staticmethod
    def rotl32(original, shift): # CAN'T DO >>> IN PYTHON
        #return ((original << shift) & Murmur3.UINT_MASK) | ((original >>> (32 - shift)) * Murmur3.UINT_MASK)
        return ((original << shift) & Murmur3.UINT_MASK) | ((original % 0x100000000) >> (32 - shift))

    @staticmethod
    def fmix32(h):
        h ^= (h >> 16) & Murmur3.UINT_MASK
        h = (h * 0x85ebca6b) & Murmur3.UINT_MASK
        h ^= (h >> 13) & Murmur3.UINT_MASK
        h = (h * 0xc2b2ae35) & Murmur3.UINT_MASK
        h ^= (h >> 16) & Murmur3.UINT_MASK
        return h

    @staticmethod
    def fmix64(k):
        k ^= (k % 0x100000000) >> 33
        k = (k * 0xff51afd7ed558ccd)
        k ^= (k % 0x100000000) >> 33
        k = (k * 0xc4ceb9fe1a85ec53)
        k ^= (k % 0x100000000) >> 33
        return k

def main():
    num_inputs = int(input())
    num_checks = int(input())
    bf = BloomFilter(num_inputs)

    for _ in range(num_inputs):
        s = input().strip()
        bf.add_string(s)

    in_ = 0

    for _ in range(num_checks):
        s = input().strip()
        if bf.contains(s):
            in_ += 1

    print(in_)

if __name__ == "__main__":
    main()