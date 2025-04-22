#include <iostream>
#include <math.h>
#include <bitset>
#include <vector>
#include <string>

using namespace std;

template <class T>
inline void hash_combine(std::size_t& seed, const T& v)
{
    std::hash<T> hasher;
    seed ^= hasher(v) + 0x9e3779b9 + (seed<<6) + (seed>>2);
}

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
        this->m = this->getMByP(0.001, n);
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
    void add(string n) {
        for (int i = 0; i < k; ++i) {
            size_t s = this->seeds[i];
            hash_combine(s, n);
            this->bit[s % m] = true;
        }
    }

    // method to add an int that can be deleted
    void addCollision(string n) {
        for (int i = 0; i < k; ++i) {
            size_t s = this->seeds[i];
            hash_combine(s, n);
            if (this->bit[s % m] == true)
                this->collisions[s % m] = true;
            else 
                this->bit[s % m] = true;
        }
    }

    void del(string n) {
        for (int i = 0; i < k; ++i) {
            size_t s = this->seeds[i];
            hash_combine(s, n);
            if (this->collisions[s % m] == false) {
                this->bit[s % m] = false;
            }
        }
    }


    bool contains(string n) {
        for(int i = 0; i < k; i++) {
            size_t s = this->seeds[i];
            hash_combine(s, n);
            if (bit[s % m] == false) {
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
        badIPs.add(badIP);
    }

    cin >> numBadData;

    bloomFilter badData;
    badData = bloomFilter(numBadData);
    
    for (int i = 0; i < numBadData; i++) {
        string bD;
        cin >> bD;
        badData.add(bD);
    }

    cin >> numPackets;

    bloomFilter goodIPs = bloomFilter(numPackets / 3, true);

    int badMessages = 0;
    int packetCount = 0;
    string currentIP = "";

    while (packetCount < numPackets) {
        string p;
        cin >> p;
        string ipin = p.substr(0, 32);
        string data = p.substr(32, 32);

        if (packetCount == 0)
            currentIP = ipin;
        
        if (currentIP != ipin) {
            if (badMessages >= 3) {
                goodIPs.del(currentIP);
                badIPs.add(currentIP);
            }
            else {
                cout << currentIP << '\n';

                goodIPs.addCollision(currentIP);
                cout << currentIP << '\n';
            }
            badMessages = 0;
            currentIP = ipin;
        }


        if (badData.contains(data))
            badMessages++;

        packetCount++;

        if (packetCount == numPackets) {
            if (badMessages >= 3) {
                goodIPs.del(ipin);
                badIPs.add(ipin);
            }
            else
                goodIPs.add(ipin);
        }
        //goodIPs.addCollision(ipin);

    }

    cin >> numChecks;

    for (int i = 0; i < numChecks; i++) {
        string ip;
        cin >> ip;
        //  cout << ip << '\n';
        if (goodIPs.contains(ip))
            cout << 1;
        else if (badIPs.contains(ip))
            cout << 0;
        //  cout << '\n';
    }

    return 0;
}