#include "murmur3.h"
#include <iostream>
#include <math.h>
#include <bitset>
#include <vector>
#include <string> 

using namespace std;

struct bloomFilter {

    // storage for the data structure
    vector<bool> bit;

    /* storage for seeds since cannot easily store hashing functions in cpp
     * doesn't increase size of implementation since you must store hashing functions to remain consistent
     * slight increases runtime since you must calculate the hashing function from the seed every time
     */
    vector<int> seeds;

    // number of hashing functions
    int k = 0;

    // size of BIT array
    int m;

    // expected number of elements to be added
    int n = 0;

    // defaults to making bloom filter with 1% false positive rate
    bloomFilter(int n) {
        this->m = this->getMByP(0.01, n);
        this->n = n;
        this->bit.assign(this->m, false);
        k = this->optimalK(this->m, n);
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

    // sets k seed values to random numbers
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
            int s = seeds[i];
            uint32_t h = hash(n, s); // gets k hashes and sets relevant indices to true in bit
            bit[h % m] = true;
        }
    }

    // wrapper for int hashing
    uint32_t hash(void *n, int seed) {
        void *i = &n;
        uint32_t o[4];
        MurmurHash3_x86_32(n, 8, seed, o);
        return *(uint32_t*)o; 
    }

    // checks if bf contains a value
    bool contains(void *n) {
        for(int i = 0; i < k; i++) {
            int s = seeds[i];
            uint32_t h = hash(n, s);
            if (bit[h % m] == false) { // if any index is false, return early
                return false;
            }
        }
        return true; // if all hashed indices are true, return true
    }
};

int main() {
    long numToAdd;
    long numToTest;

    cin >> numToAdd;
    cin >> numToTest;

    bloomFilter bf = bloomFilter(numToAdd);
    
    // reads in and adds values to bloom filter
    for (long i = 0; i < numToAdd; i++) {
        long toAdd;
        cin >> toAdd;
        bf.add(&toAdd);
    }

    int in = 0;

    // checks if test object is in the bloom filter
    for (long i = 0; i < numToTest; i++) {
        long toTest;
        cin >> toTest;
        if (bf.contains(&toTest))
            in++;
    }

    cout << "in: " << in << '\n';
    cout << "out: " << numToTest - in << '\n';
    return 0;
}