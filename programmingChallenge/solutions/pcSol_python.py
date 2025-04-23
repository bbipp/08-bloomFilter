import math
import random
import hashlib
import mmh3

IPMASK = 0xffffffff
random.seed(42)

def hash_combine(seed, v):
    v_hash = mmh3.hash(v, seed) & 0xffffffff # uses mmh3.hash with the current seed on v and then mask to 32 bits
    new_seed = seed ^ (v_hash + 0x9e3779b9 + (seed << 6) + (seed >> 2)) # combine the seed and v_hash with bit arithmetic similar to the C++ code...NOT REQUIRED
    return new_seed

class BloomFilter:
    def __init__(self, n, m=None, P=0.01, col=None):
        """
        n: Expected number of elements.
        m: Size of counter array. If None, computed from false positive
           probability P using m = -(n * ln(P)) / (ln2)^2.
        P: Target false positive probability.
        collisions: Keeps track of bits that have multiple elements mapped to it
        bit: Bloom Filter array representation
        k: Number of hash functions
        """
        self.n = n
        self.m = m if m is not None else self.get_m_by_p(P, n)
        self.collisions = ([False] * self.m) if col is not None else None
        self.bit = [False] * self.m
        self.k = self.optimal_k(self.m, n)
        self.set_seeds(self.k)

    # sets k seed values to random numbers
    def set_seeds(self, k):
        self.k = k
        rng = random.Random(42) 
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

    # insertion for a string
    def add_string(self, n):
        for i in range(self.k): # go through all the hash functions
            s = self.seeds[i]
            s = hash_combine(s, n) # get the index from the current hash function
            self.bit[s % self.m] = True # change the corresponding bit in the bit array to be True

    def contains(self, n): 
        for i in range(self.k): # go through k hash filters
            s = self.seeds[i] 
            s = hash_combine(s, n) # get index by hashing element for current hash "seed"
            if not self.bit[s % self.m]:
                return False
        return True # element only in filter if every index mapped by the hashing functions has been set to True

    # method to add an string that can be deleted
    def add_collision(self, n: str):
        for i in range(self.k): # go through k hash filters
            s = self.seeds[i]
            s = hash_combine(s, n) # get index by hashing element for current hash "seed"
            index = s % self.m
            if self.bit[index]: # bit already corresponds to element so there is now a collision
                self.collisions[index] = True
            else:
                self.bit[index] = True

    # delete an element
    def delete(self, n):
        for i in range(self.k): # go through k hash filters
            s = self.seeds[i]
            s = hash_combine(s, n) # get index by hashing element for current hash "seed"
            if self.collisions[s% self.m] is False: # can only delete if bit isn't shared with another element (collision)
                self.bit[s % self.m] = False

def read_non_empty_line():
    line = input().strip()
    while line == "":
        line = input().strip()
    return line

def main():
    num_bad_ips = int(read_non_empty_line())
    # all below lines that follow this syntax construct a bloom filter with error rate 0.0001%, resulting in fairly accurate results
    bad_ips_bf = BloomFilter(n=num_bad_ips, P=0.00001)

    # adds all read in bad IPs to badIPs bloom filter for later comparisons
    for i in range(num_bad_ips):
        bad_ip = read_non_empty_line()
        bad_ips_bf.add_string(bad_ip)

    num_bad_data_packets = int(read_non_empty_line())
    bad_data_packets_bf = BloomFilter(n=num_bad_data_packets, P=0.00001)

    # adds all read in bad data to badData bloom filter
    for i in range(num_bad_data_packets):
        bd = read_non_empty_line()
        bad_data_packets_bf.add_string(bd)

    num_packets_to_test = int(read_non_empty_line())
    good_ips_bf = BloomFilter(num_packets_to_test, col=True)

    bad_messages = 0
    packet_count = 0
    current_ip = ""

    # this is the important section that handles deletions and insertions
    while packet_count < num_packets_to_test:
        p = read_non_empty_line() # packet

        # separates packet into ip and data
        ipin = p[:32]
        data = p[32:64]

        # initializes packet_count
        if packet_count == 0:
            current_ip = ipin

        if current_ip != ipin: # checks if IP has changed from last line of input, indicating the end of a block
            if bad_messages >= 3: # IP address is now blacklisted
                # check if already in goodIPs. 
                # if it is not and would collide with a member, would create false negatives, which is undesireable
                if good_ips_bf.contains(current_ip):
                    good_ips_bf.delete(current_ip)

                bad_ips_bf.add_string(current_ip)
            else:
                # same with this, if the IP is already in the bad category, even if it is a collision, it will stay there
                # so no reason to add it to the good bloom filter as this can prevent values from being removed in the future
                if not bad_ips_bf.contains(current_ip):
                    good_ips_bf.add_collision(current_ip)
            # resets tracking variables
            bad_messages = 0
            current_ip = ipin

        # increment counter if data is in the bad data bloom filter
        if bad_data_packets_bf.contains(data):
            bad_messages += 1

        packet_count += 1

        # catches last line of input edge case, same logic as above
        if packet_count == num_packets_to_test:
            if bad_messages >= 3:
                good_ips_bf.delete(ipin)
                bad_ips_bf.add_string(ipin)
            else:
                good_ips_bf.add_string(ipin)

    num_checks = int(read_non_empty_line())

    # simple check for membership after setting all members previously
    # badIPs is done first to ensure that if there is a collision and a value is 
    # a member of both, it defaults to bad per the writeup
    for i in range(num_checks):
        ip = read_non_empty_line()
        if bad_ips_bf.contains(ip):
            print(0, end='')
        elif good_ips_bf.contains(ip):
            print(1, end='')

if __name__ == "__main__":
    main()