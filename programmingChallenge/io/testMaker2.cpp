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
        cout << bitset<32>(this->source) << bitset<32>(this->data) << '\n';
    }
};

int getRandFromSet(unordered_set<int> s) {
    int size = s.size();
    auto p = next(s.begin(), rand() % size);
    return *p;
}


vector<Packet> makeSeries(int source, int total, unordered_set<int> badData) {
    vector<Packet> p;
    vector<int> index = {0, 0};
  
    for (int i = 1; i <= total; i++) {
        p.push_back(Packet(source, i, total, generateRand32()));
    }

    return p;
}

vector<Packet> makeBadSeries(int source, int total, unordered_set<int> badData) {
    vector<Packet> p;
    vector<int> index;

    int numBad = rand() % (total + 1 - 3) + 4;
    index.assign(numBad, 0);

    for (int i = 1; i <= total; i++) {
        p.push_back(Packet(source, i, total, generateRand32()));
    }

    int f = -1;
    int s = -1;
    int t = -1;

    for (int i = 0; i < numBad; i++) {
        index[i] = getRandFromSet(badData);
        int loc = (rand() % (total - 1));
        while (loc == f || loc == s || loc == t)
            loc = (rand() % total);
        if (i == 0)
            f = loc;
        else if (i == 1)
            s = loc;
        else if (i == 3)
            t = loc;
        p[loc] = Packet(source, loc + 1, total, index[i]);
        
    }

    return p;
}

int main(int argc, char *argv[]) {
    std::random_device rd;    
    std::mt19937_64 eng(rd()); 
    std::uniform_int_distribution<unsigned long long> distr;
  
    long long a = (distr(eng) + 2) % (long)(pow(2, 10)) + 2;
    long long b = (distr(eng) + 2) % (long)(pow(2, 10)) + 2;
    long long p = (distr(eng) + 4) % (long)(pow(2, 10)) + 4;
    long long u = (distr(eng) + 2) % (long)(pow(2, 10)) + 2;

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

    cout << p << '\n';

    unordered_set<int> goodIP;
    vector<int> ips;
    while (p > 0) {
        int size = rand() % (4) + 1;
        p -= size;
        vector<Packet> packets;
        int ip;
        if (rand() % 2) {
            ip = generateRand32();
            ips.push_back(ip);
        }
        else
            ip = ips[rand() % ips.size()];
        if (rand() % 2 && size >= 3) {
            packets = makeBadSeries(ip, size, badData);
            badIP.insert(ip);
        }
        else {
            packets = makeSeries(ip, size, badData);
            goodIP.insert(ip);
        }
        for (int i = 0; i < size; i++) {
            packets[i].print();
        }
    }


    string output;
    cin >> output;
    ofstream expectedOutput;
    expectedOutput.open(output);

    cout << u << '\n';

    int numBad = 0;
    int numGood = 0;
    for (long long i = 0; i < u; i++) {
        int ip = rand();
        if ((rand() % 2) && numBad < a) {
            auto f = next(badIP.begin(), numBad);
            cout << bitset<32>(*f) << '\n';
            numBad++;
            expectedOutput << 0;
        }
        else if ((rand() % 3) && numGood < goodIP.size()) {
            auto g = next(goodIP.begin(), numGood);
            cout << bitset<32>(*g) << '\n';
            numGood++;
            expectedOutput << 1;
        }
        else {
            cout << bitset<32>(ip) << '\n';
        }
    }
}
