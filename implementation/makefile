all:
	make java
	make cpp

java: bloomFilter.java
	javac bloomFilter.java

python: bloomFilter.py
	python3 bloomFilter.py

cpp: bloomFilter.cpp
	g++ -o bloomFilter bloomFilter.cpp murmur3.c