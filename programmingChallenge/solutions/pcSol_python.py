import math
import random
import hashlib
import mmh3

IPMASK = 0xffffffff
random.seed(42)

def hash_combine(seed, v):
    v_hash = mmh3.hash(v, seed) & 0xffffffff
    #new_seed = seed ^ (v_hash + 0x9e3779b9 + (seed << 6) + (seed >> 2))
    new_seed = seed ^ (v_hash + 0x9e3779b9 + (seed << 6) + (seed >> 2))
    return new_seed

class BloomFilter:
    def __init__(self, n, m=None, P=0.01, col=None):
        self.n = n
        self.m = m if m is not None else self.get_m_by_p(P, n)
        self.collisions = ([False] * self.m) if col is not None else None
        self.bit = [False] * self.m
        self.k = self.optimal_k(self.m, n)
        self.set_seeds(self.k)

    def set_seeds(self, k):
        self.k = k
        rng = random.Random(42)  # Create a separate RNG instance
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

    def add_string(self, n):
        for i in range(self.k):
            s = self.seeds[i]
            s = hash_combine(s, n)
            self.bit[s % self.m] = True

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

    def contains(self, n):
        for i in range(self.k):
            s = self.seeds[i]
            s = hash_combine(s, n)  # use string hash here
            if not self.bit[s % self.m]:
                return False
        return True

    def add_collision(self, n: str):
        for i in range(self.k):
            s = self.seeds[i]
            s = hash_combine(s, n)
            index = s % self.m
            if self.bit[index]:
                self.collisions[index] = True
            else:
                self.bit[index] = True

    def delete(self, n):
        for i in range(self.k):
            s = self.seeds[i]
            s = hash_combine(s, n) # same thing as with add_collision
            if self.collisions[s% self.m] is False:
                self.bit[s % self.m] = False

def get_data(packet):
    return IPMASK & packet

def get_ip(packet):
    return IPMASK & (packet >> 32)

def read_non_empty_line():
    line = input().strip()
    while line == "":
        line = input().strip()
    return line

def main():
    num_bad_ips = int(read_non_empty_line())
    bad_ips_bf = BloomFilter(n=num_bad_ips, P=0.00001)

    for i in range(num_bad_ips):
        bad_ip = read_non_empty_line()
        bad_ips_bf.add_string(bad_ip)

    num_bad_data_packets = int(read_non_empty_line())
    bad_data_packets_bf = BloomFilter(n=num_bad_data_packets, P=0.00001)

    for _ in range(num_bad_data_packets):
        bd = read_non_empty_line()
        bad_data_packets_bf.add_string(bd)

    num_packets_to_test = int(read_non_empty_line())
    good_ips_bf = BloomFilter(num_packets_to_test, col=True)

    bad_messages = 0
    packet_count = 0
    current_ip = ""

    while packet_count < num_packets_to_test:
        p = read_non_empty_line() # packet
        ipin = p[:32]
        data = p[32:64]

        if packet_count == 0:
            current_ip = ipin

        if current_ip != ipin:
            if bad_messages >= 3: # IP address is now blacklisted
                if good_ips_bf.contains(current_ip):
                    good_ips_bf.delete(current_ip)

                bad_ips_bf.add_string(current_ip)
            else:
                if not bad_ips_bf.contains(current_ip):
                    good_ips_bf.add_collision(current_ip)
            bad_messages = 0
            current_ip = ipin

        if bad_data_packets_bf.contains(data):
            bad_messages += 1

        packet_count += 1

        if packet_count == num_packets_to_test:
            if bad_messages >= 3:
                good_ips_bf.delete(ipin)
                bad_ips_bf.add_string(ipin)
            else:
                good_ips_bf.add_string(ipin)

    num_checks = int(read_non_empty_line())

    for i in range(num_checks):
        ip = read_non_empty_line()
        if bad_ips_bf.contains(ip):
            print(0, end='')
        elif good_ips_bf.contains(ip):
            print(1, end='')

if __name__ == "__main__":
    main()