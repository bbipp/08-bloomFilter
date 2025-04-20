#include <iostream>
#include <math.h>
#include <bitset>
#include <vector>
#include <string> 
#include <random>
#include <unordered_set>
#include <fstream>
#include <algorithm>

using namespace std;


int generateRand32() {
    return (int)rand();
}

struct Packet {
    int source;
    int seq;
    int total;
    int data;

    Packet(int source, int seq, int total, int data) {
        this->source = source;
        this->seq = seq;
        this->total = total;
        this-> data = data;
    }

    void print() {
        cout << bitset<32>(this->source) << bitset<32>(this->seq) << bitset<32>(this->total) << bitset<32>(this->data) << '\n';
    }
};

vector<Packet> makeSeries(int source, int total) {
    vector<Packet> p;
    for (int i = 1; i <= total; i++) {
        p.push_back(Packet(source, i, total, generateRand32()));
    }
    return p;
}

int main(int argc, char *argv[]) {
    std::random_device rd;    
    std::mt19937_64 eng(rd()); 
    std::uniform_int_distribution<unsigned long long> distr;
  
    long long a = (distr(eng) + 2) % (long)(pow(2, 20));
    long long b = (distr(eng) + 2) % (long)(pow(2, 11));
    long long p = (distr(eng) + 4) % (long)(pow(2, 500));
    long long u = (distr(eng) + 2) % (long)(pow(2, 20));

    if (argc >= 2) {
        a = stoll(argv[1]);
        b = stoll(argv[2]);
        p = stoll(argv[3]);
        u = stoll(argv[4]);
    }

    srand(time(0));

    unordered_set<int> badIP;
    cout << a << '\n';
    for (long long i = 0; i < a; i++) {
        int ip = rand();
        badIP.insert(ip);
        cout << bitset<32>(ip) << '\n';
    }

    unordered_set<int> badData;
    cout << b << '\n';
    for (long long i = 0; i < b; i++) {
        int data = rand();
        badData.insert(data);
        cout << bitset<32>(data) << '\n';
    }



    ofstream expectedOutput;
    expectedOutput.open ("out.txt");

    cout << p << '\n';

    int numBad = 0;
    for (long long i = 0; i < u; i++) {
        int ip = rand();
        if ((rand() % 2 || (badIP.find(ip) != badIP.end())) && numBad < a) {
            auto f = next(badIP.begin(), numBad);
            cout << bitset<32>(*f) << '\n';
            numBad++;
            expectedOutput << 1;
        }
        else {
            cout << bitset<32>(ip) << '\n';
            expectedOutput << 0;
        }
    }
}