#include "murmur3.h"
#include <iostream>
#include <math.h>
#include <bitset>
#include <vector>
#include <string> 

using namespace std;

int IPMASK = 0xffffffff;

class bloomFilter {
    public:
    vector<bool> bit;

    vector<int> seeds;

    vector<bool> collisions;

    // number of hashing functions
    int k = 0;

    // size of BIT array
    int m;

    // expected number of elements to be added
    int n = 0;

    bloomFilter() {
    }

    // defaults to making bloom filter with 1% false positive rate
    bloomFilter(int n) {
        this->m = this->getMByP(0.01, n);
        this->n = n;
        this->bit.assign(this->m, false);
        this->k = this->optimalK(this->m, n);
        setSeeds(k);
    }

    bloomFilter(int n, bool col) {
        this->m = this->getMByP(0.01, n);
        this->n = n;
        this->collisions.assign(this->m, false);
        this->bit.assign(this->m, false);
        this->k = this->optimalK(this->m, n);
        setSeeds(k);
    }

    // creates bloomFilter at specific P
    bloomFilter(float P, int n) {
        this->m = this->getMByP(P, n);
        this->n = n;
        this->bit.assign(this->m, false);
        this->k = this->optimalK(this->m, n);
        setSeeds(this->k);
    }

    // creates a bloomFilter of size m
    bloomFilter(int m, int n) {
        this->m =  m;
        this->n = n;
        this->bit.assign(this->m, false);
        this->k = this->optimalK(this->m, n);
        setSeeds(this->k);
    }

    void setSeeds(int k) {
        this->k = k;
        srand(time(0));
        for(int i = 0; i < k; i++) {
            this->seeds.push_back(rand());
        }
    }

    // calculates the probability of false positive
    int getProb() {
        return (int)pow(1 - pow((1 - (1 / m)), k * n), k);
    }

    // sets m to guarantee a probability P on n inputs
    int getMByP(double P, int n) {
        return (int)-((n * log(P)) / pow(log(2), 2));
    }

    // sets m to any integer
    void setM(int m) {
        this->m = m;
    }

    // sets n to any integer
    void setN(int n) {
        this->n = n;
    }

    // returns optimal number of hashing functions given n and m
    int optimalK(int m, int n) {
        return (int)((this->m / this->n) * log(2));
    }

    // method to add an int
    void add(void *n) {
        for (int i = 0; i < k; ++i) {
            int s = this->seeds[i];
            uint32_t h = hash(n, s);
            this->bit[h % m] = true;
        }
    }

    // method to add an int that can be deleted
    void addCollision(void *n) {
        for (int i = 0; i < k; ++i) {
            int s = this->seeds[i];
            uint32_t h = hash(n, s);
            if (this->bit[h % m] == true)
                this->collisions[h % m] = true;
        }
    }

    void del(void *n) {
        for (int i = 0; i < k; ++i) {
            int s = this->seeds[i];
            uint32_t h = hash(n, s);
            if (this->collisions[h % m] == false) {
                this->bit[h % m] = false;
            }
        }
    }

    // wrapper for int hashing
    uint32_t hash(void *n, int seed) {
        double i = stod(*(string *)n);
        uint32_t o[4];
        MurmurHash3_x86_32(n, 32, seed, o);
        cout << *o << '\n';
        fflush(stdout);
        return *(uint32_t*)o; 
    }

    bool contains(void *n) {
        for(int i = 0; i < k; i++) {
            int s = this->seeds[i];
            uint32_t h = hash(n, s);
            if (bit[h % m] == false) {
                return false;
            }
        }
        return true;
    }
};

int getData(long long packet) {
    return IPMASK & packet;
}

int getIP(long long packet) {
    return IPMASK & (packet >> 32);
}

int main() {
    int numBadIP, numBadData, numPackets, numChecks;
    cin >> numBadIP;

    bloomFilter badIPs;
    badIPs = bloomFilter(numBadIP);

    for (int i = 0; i < numBadIP; i++) {
        string badIP;
        cin >> badIP;
        badIPs.add(&badIP);
    }

    // cin >> numBadData;

    // bloomFilter badData;
    // badData = bloomFilter(numBadData);
    
    // for (int i = 0; i < numBadData; i++) {
    //     string bD;
    //     cin >> bD;
    //     badData.add(&bD);
    // }

    // cin >> numPackets;

    // bloomFilter goodIPs = bloomFilter(numPackets / 3);
    // bloomFilter oneStrike = bloomFilter(numPackets / 3);
    // bloomFilter twoStrike = bloomFilter(numPackets / 3);

    // int curIP = -1;

    // for (int i = 0; i < numPackets; i++) {
    //     string p;
    //     cin >> p;
        
    // }

    cin >> numChecks;

    for (int i = 0; i < numChecks; i++) {
        string ip;
        cin >> ip;

        // if (goodIPs.contains(&ip))
        //     cout << 1;
        // else 
        cout << "ans: " << badIPs.contains(&ip) << '\n';


    }
fflush(stdout);

    return 0;
}