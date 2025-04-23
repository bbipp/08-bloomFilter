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

    // makes a bloom filter with a collision array, allowing for deletions with no false negatives
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

    // method to add a value
    void add(string n) {
        for (int i = 0; i < k; ++i) {
            size_t s = this->seeds[i];
            hash_combine(s, n);
            this->bit[s % m] = true;
        }
    }

    /* 
    * method to add a value that can be deleted
    * this is done by checking if the index that would be set
    * to true is already true, and then setting the collision
    * array to true in that location instead
    */
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

    // delete method checks against collision array, and resets bits with no collisions
    void del(string n) {
        for (int i = 0; i < k; ++i) {
            size_t s = this->seeds[i];
            hash_combine(s, n);
            if (this->collisions[s % m] == false) {  // checks if multiple added values correspond to a single index
                this->bit[s % m] = false;
            }
        }
    }

    // checks if a value is present by verifying it against all indices it hashes to
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

int main() {
    int numBadIP, numBadData, numPackets, numChecks;
    cin >> numBadIP;

    bloomFilter badIPs;

    // all below lines that follow this syntax construct a bloom filter with error rate 0.0001%, resulting in fairly accurate results
    badIPs = bloomFilter((float)0.00001, numBadIP);

    // adds all read in bad IPs to badIPs bloom filter for later comparisons
    for (int i = 0; i < numBadIP; i++) {
        string badIP;
        cin >> badIP;
        badIPs.add(badIP);
    }

    cin >> numBadData;

    bloomFilter badData;
    badData = bloomFilter((float)0.00001, numBadData);
    
    // adds all read in bad data to badData bloom filter
    for (int i = 0; i < numBadData; i++) {
        string bD;
        cin >> bD;
        badData.add(bD);
    }

    cin >> numPackets;

    bloomFilter goodIPs = bloomFilter(numPackets, true);

    int badMessages = 0;
    int packetCount = 0;
    string currentIP = "";

    // this is the important section that handles deletions and insertions
    while (packetCount < numPackets) {
        string p;
        cin >> p;

        // separates packet into ip and data
        string ipin = p.substr(0, 32);
        string data = p.substr(32, 32);

        // initializes packetCount
        if (packetCount == 0)
            currentIP = ipin;
        
        // checks if IP has changed from last line of input, indicating the end of a block
        if (currentIP != ipin) {
            // check for if the last block contained more than 3 bad messages
            if (badMessages >= 3) {
                // check if already in goodIPs. 
                // if it is not and would collide with a member, would create false negatives, which is undesireable
                if (goodIPs.contains(currentIP))
                    goodIPs.del(currentIP);
                badIPs.add(currentIP);
            }
            else {
                // same with this, if the IP is already in the bad category, even if it is a collision, it will stay there
                // so no reason to add it to the good bloom filter as this can prevent values from being removed in the future
                if (!badIPs.contains(currentIP))
                    goodIPs.addCollision(currentIP);
            }

            // resets tracking variables
            badMessages = 0;
            currentIP = ipin;
        }

        // increment counter if data is in the bad data bloom filter
        if (badData.contains(data)) {
            badMessages++;
        }

        packetCount++;

        // catches last line of input edge case, same logic as above
        if (packetCount == numPackets) {
            if (badMessages >= 3) {
                if (goodIPs.contains(currentIP))
                    goodIPs.del(ipin);
                badIPs.add(ipin);
            }
            else
                if (!badIPs.contains(currentIP))
                    goodIPs.add(ipin);
        }
    }

    cin >> numChecks;

    // simple check for membership after setting all members previously
    // badIPs is done first to ensure that if there is a collision and a value is 
    // a member of both, it defaults to bad per the writeup
    for (int i = 0; i < numChecks; i++) {
        string ip;
        cin >> ip;
        if (badIPs.contains(ip))
            cout << 0;
        else if (goodIPs.contains(ip))
            cout << 1;
    }

    return 0;
}