#include <iostream>

using namespace std;

struct Packet {
    unsigned int source;
    unsigned int seq;
    unsigned int total;
    unsigned int data;

    Packet(unsigned short source, unsigned int seq, unsigned int total, unsigned int data) {
        this->source = source;
        this->seq = seq;
        this->total = total;
        this-> data = data;
    }

    void print() {
        cout << this->source << this->seq << this->data;
    }
};

int main() {

    return 0;
}