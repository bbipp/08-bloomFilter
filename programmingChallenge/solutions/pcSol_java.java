import java.math.BigInteger;
import java.nio.ByteOrder;
import java.util.concurrent.ThreadLocalRandom;
import java.util.*;
import java.nio.ByteBuffer;

class bloomFilter {
    // storage for the data structure
    public boolean[] bit;

    /* storage for seeds since cannot easily store hashing functions in java
     * doesn't increase size of implementation since you must store hashing functions to remain consistent
     * slight increases runtime since you must calculate the hashing function from the seed every time
     */
    private long[] seeds;

    private boolean[] collisions;

    // number of hashing functions
    public int k;

    // size of BIT array
    public int m;

    // expected number of elements to be added
    private int n = 0;

    // defaults to making bloom filter with 1% false positive rate
    bloomFilter(int n) {
        this.m = this.getMByP(0.01, n);
        this.n = n;
        bit = new boolean[this.m];
        this.k = this.optimalK(this.m, n);
        setSeeds(this.k);
    }

    // creates a bloom filter and initialized collisions array
    bloomFilter(int n, boolean col) {
        this.m = this.getMByP(0.01, n);
        this.n = n;
        this.collisions = new boolean[this.m];
        Arrays.fill(this.collisions, false);
        this.bit = new boolean[this.m];
        Arrays.fill(this.bit, false);
        this.k = this.optimalK(this.m, n);
        setSeeds(k);
    }

    // creates bloomFilter at specific P
    bloomFilter(float P, int n) {
        this.m = this.getMByP(P, n);
        this.n = n;
        bit = new boolean[this.m];
        this.k = this.optimalK(this.m, n);
        setSeeds(this.k);
    }

    // creates a bloomFilter of size m
    bloomFilter(int m, int n) {
        this.m = m;
        this.n = n;
        bit = new boolean[this.m];
        this.k = this.optimalK(m, n);
        setSeeds(this.k);
    }

    // initializes the array of seeds that will be referenced continually
    public void setSeeds(int k) {
        this.k = k;
        seeds = new long[k];
        for(int i = 0; i < k; i++) {
            seeds[i] = ThreadLocalRandom.current().nextLong();
        }
    }

    // calculates the probability of false positive
    public int getProb() {
        return (int)Math.pow(1 - Math.pow((1 - (1 / m)), k * n), k);
    }

    // sets m to guarantee a probability P on n inputs
    public int getMByP(double P, int n) {
        return (int)-((n * Math.log(P)) / Math.pow(Math.log(2), 2));
    }

    // sets m to any integer
    public void setM(int m) {
        this.m = m;
    }

    // sets n to any integer
    public void setN(int n) {
        this.n = n;
    }

    // returns optimal number of hashing functions given n and m
    public int optimalK(int m, int n) {
        return (int)((this.m / this.n) * Math.log(2));
    }

    // method to add a string
    public void add(String s) {
        for(int i = 0; i < k; i++) {
            long h = hash(s, seeds[i]);
            bit[(int) (h % (long)m)] = true;
        }
    }

    // wrapper for string hashing
    public long hash(String s, long seed) {
        byte[] m = s.getBytes();
        return Murmur3.hash_x86_32(m, s.length(), seed);
    }

    // method to add an int
    public void add(int n) {
        for(int i = 0; i < k; i++) {
            long h = hash(n, seeds[i]);
            bit[(int) (h % (long)m)] = true;
        }
    }

    // wrapper for int hashing
    public long hash(int n, long seed) {
        BigInteger bigInt = BigInteger.valueOf(n);      
        byte[] b = bigInt.toByteArray();
        return Murmur3.hash_x86_32(b, b.length, seed);
    }

    // method to add an int that can be deleted
    void addCollision(String n) {
        for (int i = 0; i < k; ++i) {
            long h = hash(n, seeds[i]);
            int index = (int) (h % (long)m);
            if (this.bit[index]) {
                this.collisions[index] = true;
            } else {
                this.bit[index] = true;
            }
        }
    }

    // method to remove an int without affecting the validity of the bloom filter
    void del(String n) {
        for (int i = 0; i < k; ++i) {
            long h = hash(n, seeds[i]);
            if (this.collisions[(int) (h % (long)m)] == false) {
                this.bit[(int) (h % (long)m)] = false;
            }
        }
    }

    // method to check if an int is stored in the bloom filter
    public boolean contains(int n) {
        for(int i = 0; i < k; i++) {
            long h = hash(n, seeds[i]);
            if (bit[(int) (h % (long)m)] == false) {
                return false;
            }
        }
        return true;
    }

    // method to check if an int (string form) is stored in the bloom filter 
    public boolean contains(String s) {
        for(int i = 0; i < k; i++) {
            long h = hash(s, seeds[i]);
            if (bit[(int) (h % (long)m)] == false) {
                return false;
            }
        }
        return true;
    }
}

public class pcSol_java {
    public static void main(String[] args) {
        // initialize scanner that will read in input
        Scanner scanner = new Scanner(System.in);

        // read in the number of initial bad IP addresses
        int numBadIP = scanner.nextInt();

        // initialize a bloomfilter with a 0.00001 probability of a false positive
        bloomFilter badIPs = new bloomFilter((float)0.00001, numBadIP);
        String badIP = scanner.nextLine(); // eat new line character

        //add each bad IP to the badIP bloomfilter
        for (int a = 0; a<numBadIP; a++) {
            badIP = scanner.nextLine();
            badIPs.add(badIP);
        }

        // read in the number of bad data
        int numBadData = scanner.nextInt();

        // initialize a bloomfilter with a 0.00001 probability of a false positive
        bloomFilter badData = new bloomFilter((float)0.00001, numBadData);
        String bData = scanner.nextLine(); // eat new line character

        //add each bad data to the badData bloomfilter
        for (int b = 0; b<numBadData; b++) {
            bData = scanner.nextLine();
            badData.add(bData);
        }

        // read in the number of packets that need to be tested
        int numPackets = scanner.nextInt();

        // initialize a bloomfilter with a 0.01 probability of a false positive 
        // and initialize the collisions array
        bloomFilter goodIPs = new bloomFilter(numPackets, true);

        int badMessages = 0;
        int packetCount = 0;
        String currentIP = "";

        //initialize the output string
        String res = "";

        String p = scanner.nextLine(); // eat new line character

        //process each incoming packet
        while (packetCount < numPackets) {
            p = scanner.nextLine();
            String ipin = p.substring(0, 32); //split by source IP address
            String data = p.substring(32, 64); //split by data bitstring

            if (packetCount == 0)
                currentIP = ipin;
        
            if (!currentIP.equals(ipin)) {
                // if the IP address has sent at least 3 bad data, remove it from the bloom filter of good IPs and add to the bloom filters of bad IPs
                if (badMessages >= 3) {
                    if (goodIPs.contains(currentIP))
                        goodIPs.del(currentIP);
                    badIPs.add(currentIP);
                } else {
                    if (!badIPs.contains(currentIP))
                        goodIPs.addCollision(currentIP);
                }
                badMessages = 0;
                currentIP = ipin;
            }
    
            //increase badMessages counter if the packet data is in the bad data bloom filter
            if (badData.contains(data)) {
                badMessages++;
            }
    
            packetCount++;
    
            // update good and bad IP bloom filters
            if (packetCount == numPackets) {
                if (badMessages >= 3) {
                    goodIPs.del(ipin);
                    badIPs.add(ipin);
                }
                else
                    goodIPs.add(ipin);
            }    
        }

        // read in the number of queries
        int numChecks = scanner.nextInt();

        String ip = scanner.nextLine(); // eat new line character

        // process each query and store:
            // 0 if the source IP is bad
            // 1 if the source ID is good
            // nothing if the source ID did not make a request
        for (int i = 0; i < numChecks; i++) {
            ip = scanner.nextLine();

            if (badIPs.contains(ip)) {
                res = res + "0";
            } else if (goodIPs.contains(ip)) {
                res = res + "1";
            }
        }

        // print result
        System.out.print(res);

        scanner.close();
    }
}

/* murmur3 hashing algorithm implementation taken from
 * https://github.com/sangupta/murmur/blob/master/src/main/java/com/sangupta/murmur/Murmur3.java
 * murmur3 is not cryptographically strong but it is fast and reliable
 */
class Murmur3 {
	/** 
     * Helps convert a byte into its unsigned value
	 */
	public static final int UNSIGNED_MASK = 0xff;

	/**
	 * Helps convert integer to its unsigned value
	 */
	public static final long UINT_MASK = 0xFFFFFFFFl;
	
	/**
	 * Helps convert long to its unsigned value
	 */
	public static final long LONG_MASK = 0xFFFFFFFFFFFFFFFFL;
     private static final int X86_32_C1 = 0xcc9e2d51;
     
     private static final int X86_32_C2 = 0x1b873593;
     
     private static long X64_128_C1 = 0x87c37b91114253d5L;
     
     private static long X64_128_C2 = 0x4cf5ad432745937fL;
 
     /**
      * Compute the Murmur3 hash as described in the original source code.
      * 
      * @param data
      *            the data that needs to be hashed
      * 
      * @param length
      *            the length of the data that needs to be hashed
      * 
      * @param seed
      *            the seed to use to compute the hash
      * 
      * @return the computed hash value
      */
     public static long hash_x86_32(final byte[] data, int length, long seed) {
         final int nblocks = length >> 2;
         long hash = seed;
         
         //----------
         // body
         for(int i = 0; i < nblocks; i++) {
             final int i4 = i << 2;
             
             long k1 = (data[i4] & UNSIGNED_MASK);
             k1 |= (data[i4 + 1] & UNSIGNED_MASK) << 8;
             k1 |= (data[i4 + 2] & UNSIGNED_MASK) << 16;
             k1 |= (data[i4 + 3] & UNSIGNED_MASK) << 24;
                          
             k1 = (k1 * X86_32_C1) & UINT_MASK;
             k1 = rotl32(k1, 15);
             k1 = (k1 * X86_32_C2) & UINT_MASK;
             
             hash ^= k1;
             hash = rotl32(hash,13); 
             hash = (((hash * 5) & UINT_MASK) + 0xe6546b64l) & UINT_MASK;
         }
         
         //----------
         // tail
 
         // Advance offset to the unprocessed tail of the data.
         int offset = (nblocks << 2); // nblocks * 2;
         long k1 = 0;
         
         switch (length & 3) {
             case 3:
                 k1 ^= (data[offset + 2] << 16) & UINT_MASK;
     
             case 2:
                 k1 ^= (data[offset + 1] << 8) & UINT_MASK;
     
             case 1:
                 k1 ^= data[offset];
                 k1 = (k1 * X86_32_C1) & UINT_MASK;
                 k1 = rotl32(k1, 15);
                 k1 = (k1 * X86_32_C2) & UINT_MASK;
                 hash ^= k1;
         }
 
         // ----------
         // finalization
 
         hash ^= length;
         hash = fmix32(hash);
 
         return hash;
     }
     

     public static long[] hash_x64_128(final byte[] data, final int length, final long seed) {
         long h1 = seed;
         long h2 = seed;
 
         ByteBuffer buffer = ByteBuffer.wrap(data);
         buffer.order(ByteOrder.LITTLE_ENDIAN);
         
         while(buffer.remaining() >= 16) {
             long k1 = buffer.getLong();
             long k2 = buffer.getLong();
 
             h1 ^= mixK1(k1);
 
             h1 = Long.rotateLeft(h1, 27);
             h1 += h2;
             h1 = h1 * 5 + 0x52dce729;
 
             h2 ^= mixK2(k2);
 
             h2 = Long.rotateLeft(h2, 31);
             h2 += h1;
             h2 = h2 * 5 + 0x38495ab5;
         }
 
         buffer.compact();
         buffer.flip();
 
         final int remaining = buffer.remaining();
         if(remaining > 0) {
             long k1 = 0;
             long k2 = 0;
             switch (buffer.remaining()) {
                 case 15:
                     k2 ^= (long) (buffer.get(14) & UNSIGNED_MASK) << 48;
                 
                 case 14:
                     k2 ^= (long) (buffer.get(13) & UNSIGNED_MASK) << 40;
                 
                 case 13:
                     k2 ^= (long) (buffer.get(12) & UNSIGNED_MASK) << 32;
                 
                 case 12:
                     k2 ^= (long) (buffer.get(11) & UNSIGNED_MASK) << 24;
                 
                 case 11:
                     k2 ^= (long) (buffer.get(10) & UNSIGNED_MASK) << 16;
                 
                 case 10:
                     k2 ^= (long) (buffer.get(9) & UNSIGNED_MASK) << 8;
                 
                 case 9:
                     k2 ^= (long) (buffer.get(8) & UNSIGNED_MASK);
         
                 case 8:
                     k1 ^= buffer.getLong();
                     break;
                 
                 case 7:
                     k1 ^= (long) (buffer.get(6) & UNSIGNED_MASK) << 48;
                 
                 case 6:
                     k1 ^= (long) (buffer.get(5) & UNSIGNED_MASK) << 40;
                 
                 case 5:
                     k1 ^= (long) (buffer.get(4) & UNSIGNED_MASK) << 32;
                 
                 case 4:
                     k1 ^= (long) (buffer.get(3) & UNSIGNED_MASK) << 24;
                 
                 case 3:
                     k1 ^= (long) (buffer.get(2) & UNSIGNED_MASK) << 16;
                 
                 case 2:
                     k1 ^= (long) (buffer.get(1) & UNSIGNED_MASK) << 8;
                 
                 case 1:
                     k1 ^= (long) (buffer.get(0) & UNSIGNED_MASK);
                     break;
                     
                 default:
                     throw new AssertionError("Code should not reach here!");
             }
             
             // mix
             h1 ^= mixK1(k1);
             h2 ^= mixK2(k2);
         }
 
         // ----------
         // finalization
 
         h1 ^= length;
         h2 ^= length;
 
         h1 += h2;
         h2 += h1;
 
         h1 = fmix64(h1);
         h2 = fmix64(h2);
 
         h1 += h2;
         h2 += h1;
 
         return (new long[] { h1, h2 });
     }
     
     private static long mixK1(long k1) {
         k1 *= X64_128_C1;
         k1 = Long.rotateLeft(k1, 31);
         k1 *= X64_128_C2;
         
         return k1;
     }
 
     private static long mixK2(long k2) {
         k2 *= X64_128_C2;
         k2 = Long.rotateLeft(k2,  33);
         k2 *= X64_128_C1;
         
         return k2;
     }
 
     /**
      * Rotate left for 32 bits.
      * 
      * @param original
      * @param shift
      * @return
      */
     private static long rotl32(long original, int shift) {
         return ((original << shift) & UINT_MASK) | ((original >>> (32 - shift)) & UINT_MASK);
     }
     
     /**
      * Rotate left for 64 bits.
      * 
      * @param original
      * @param shift
      * @return
      */
     /**
      * fmix function for 32 bits.
      * 
      * @param h
      * @return
      */
     private static long fmix32(long h) {
         h ^= (h >> 16) & UINT_MASK;
         h = (h * 0x85ebca6bl) & UINT_MASK;
         h ^= (h >> 13) & UINT_MASK;
         h = (h * 0xc2b2ae35) & UINT_MASK;
         h ^= (h >> 16) & UINT_MASK;
 
         return h;
     }
     
     /**
      * fmix function for 64 bits.
      * 
      * @param k
      * @return
      */
     private static long fmix64(long k) {
         k ^= k >>> 33;
         k *= 0xff51afd7ed558ccdL;
         k ^= k >>> 33;
         k *= 0xc4ceb9fe1a85ec53L;
         k ^= k >>> 33;
 
         return k;
     }
     
 }
