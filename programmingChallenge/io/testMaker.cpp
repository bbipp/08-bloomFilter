#include <iostream>
#include <math.h>
#include <bitset>
#include <vector>
#include <string> 

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

vector<Packet> makeBadSeries(int source, int total, vector<int> badData) {
    vector<Packet> p;
    int startBad = (rand() % total) - badData.size();
    
    vector<int> randData;
    for (int i = 0; i < total; i++) {
        randData.push_back(generateRand32());
    }
    int j = 0;
    for (int i = 1; i <= total; i++) {

        if (i > startBad || i <= startBad + badData.size()) {
            p.push_back(Packet(source, i, total, badData[j]));
            j++;
        }
        else
            p.push_back(Packet(source, i, total, randData[i]));
    }
    return p;
}

int main(int argc, char *argv[]) {
    long long numDoNotServe;
    int numBitstrings;
    long long numPackets;

    cin >> numDoNotServe;
    cin >> numBitstrings;
    cin >> numPackets;

    numPackets = pow(2, numPackets);
    numPackets = numPackets - (rand() % numPackets);

    srand(time(0));
    int numGoodIP = (rand() % numPackets);

    cout << numDoNotServe << '\n';
    vector<int> doNotServeIP;
    for (int i = 0; i < numDoNotServe; i++) {
        int ip = generateRand32();
        doNotServeIP.push_back(ip);
        cout << bitset<32>(ip)<<std::endl;
    }

    cout << numBitstrings << '\n';
    vector<vector<int>> badData(numBitstrings);
    for (int i = 0; i < numBitstrings; i++) {
        int size = (rand() % 64 + 1);
        for (int j = 0; j < size; j++) {
            int data32 = generateRand32();
            badData[i].push_back(data32);
            cout << bitset<32>(data32);
        }
        cout << '\n';
    }

    long long totalIP = numGoodIP + numDoNotServe + (rand() % numPackets * pow(2, 10));

    vector<int> notSentIP;
    for (int i = 0; i < totalIP - numGoodIP - numDoNotServe; i++) {
        notSentIP.push_back(generateRand32());
    }
    
    vector<vector<Packet>> packets(numPackets);

    vector<Packet> p = makeBadSeries(generateRand32(), 2, badData[0]);

    if (argc == 1) {
        while (numPackets > 0) {
            long long nextPacketSize = numPackets % (rand() % numPackets);
            if (rand() % 2 == 1)
                packets.push_back(makeSeries())
        }
    }
    else if (*argv[1] == '1') {
        cout << "tes";
    }

    for (int i = 0; i < p.size(); i++) {
        p[i].print();
    }
    return 0;
}