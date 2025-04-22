import math
import random
import hashlib

IPMASK = 0xffffffff

class BloomFilter:
    def __init__(self, n, m=None, P=0.01, col=None):
        self.n = n
        self.m = m if m is not None else self.get_m_by_p(P, n)
        self.collisions = [False] * self.m if col is not None else self.collisions = None
        self.bit = [False] * self.m
        self.k = self.optimal_k(self.m, n)
        self.set_seeds(self.k)

    def set_seeds(self, k):
        self.k = k
        rng = random.Random()  # Create a separate RNG instance
        self.seeds = [rng.randint(0, 2147483647) for _ in range(k)]

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

    '''
    def hash_combine(self, seed, value):
        # I think this is the python equivalent of the c++ custome bit shifting for hashing
        h = hashlib.sha256((str(seed) + value).encode()).hexdigest()
        return int(h, 16)
    '''
    
    def add_string(self, s):
        for i in range(self.k):
            h = self.hash_string(s, self.seeds[i])
            self.bit[h % self.m] = True

    # wrapper for string hashing -- in python3 long is also included in int
    def hash_string(self, s, seed):
        byte_array = s.encode('utf-8')
        # created custom one in c++ but I think we can use the built-in python library
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

    # for STRING only....if need contains for an int will need to change
    def contains(self, s):
        for i in range(self.k):
            h = self.hash_string(s, self.seeds[i])  # use string hash here
            if not self.bit[h % self.m]:
                return False
        return True

    # method to add an int that can be deleted
    def add_collision(self, n: str):
        for i in range(self.k):
            seed = self.seeds[i]
            h = mmh3.hash(n, seed) & 0xffffffff # mmh3.hash returns a signed 32-bit int but we need it unsigned
            if self.bit[h % self.m] == True:
                self.collisions[h % self.m] = True

    def delete(self, n):
        for i in range(self.k):
            s = self.seeds[i]
            h = mmh3.hash(n, seed) & 0xffffffff # same thing as with add_collision
            if self.collisions[h % self.m] is False:
                self.bit[h % self.m] = False

def get_data(packet):
    return IPMASK & packet

def get_ip(packet):
    return IPMASK & (packet >> 32)

def main():
    num_bad_ips = int(input())
    bad_ips_bf = bloomFilter(num_bad_ips)

    for i in range(num_bad_ips):
        bad_ip = input()
        bad_ips_bf.add(bad_ip)

    num_bad_data_packets = int(input())
    bad_data_packets_bf = bloomFilter(num_bad_data_packets)

    for _ in range(num_bad_data_packets):
        bd = input()
        bad_data_packets_bf.add(bd)

    num_packets_to_test = int(input())
    good_ips_bf = bloomFilter(num_packets_to_test // 3, True)

    bad_messages = 0
    packet_count = 0
    current_ip = ""

    while packet_count < num_packets_to_test:
        p = input() # packet
        ipin = p[:32]
        data = p[32:64]

        if packet_count == 0:
            current_ip = ipin

        if current_ip != ipin:
            if bad_messages >= 3: # IP address is now blacklisted
                good_ips_bf.delete(current_ip)
                bad_ips_bf.add(current_ip)
            else:
                good_ips.addCollision(current_ip)
            bad_messages = 0
            current_ip = ipin

        if bad_data.contains(data):
            bad_messages += 1

        packet_count += 1

        if packet_count == num_packets:
            if bad_messages >= 3:
                good_ips.del_(ipin)
                bad_ips.add(ipin)
            else:
                good_ips.add(ipin)

        good_ips.addCollision(ipin)

    num_checks = int(input())

    for i in range(num_checks):
        ip = input()
        if good_ips.contains(ip):
            print(1, end='')
        elif bad_ips.contains(ip):
            print(0, end='')

if __name__ == "__main__":
    main()