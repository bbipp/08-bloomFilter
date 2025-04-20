#include <iostream>
#include <math.h>
#include <bitset>
#include <vector>
#include <string> 

using namespace std;

int main() {
    long numToAdd;
    long numToTest;

    cin >> numToAdd;
    cin >> numToTest;

    cout << numToAdd << ' ' << numToTest << '\n';

    srand(time(0));
    vector<long> nums;

    for (long i = 0; i < numToAdd; i++) {
        long toAdd = rand();
        cout << toAdd << '\n';
        if (nums.size() < numToTest)
            nums.push_back(toAdd);
    }

    long in = 0;
    for (long i = 0; i < numToTest; i++) {
        if (rand() % 2) {
            cout << nums[i % nums.size()] << '\n';
            in++;
        }
        else
            cout << rand() << '\n';
    }

    cout << "in: " << in << '\n';
    cout << "out: " << numToTest - in << '\n';
    return 0;
}