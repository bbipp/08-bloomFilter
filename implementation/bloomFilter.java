import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Scanner;
import java.util.concurrent.ThreadLocalRandom;

class bloomFilter {
    // storage for the data structure
    private boolean[] bit;

    /* storage for seeds since cannot easily store hashing functions in java
     * doesn't increase size of implementation since you must store hashing functions to remain consistent
     * slight increases runtime since you must calculate the hashing function from the seed every time
     */
    private long[] seeds;

    // number of hashing functions
    private int k;

    // size of BIT array
    private int m;

    // expected number of elements to be added
    private int n = 0;

    // defaults to making bllom filter with 1% false positive rate
    bloomFilter(int n) {
        this.m = this.getMByP(0.01, n);
        this.n = n;
        bit = new boolean[this.m];
        this.k = this.optimalK(this.m, n);
        setSeeds(this.k);
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

    // sets k seed values to random numbers
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
            long h = hash(s, seeds[i]);     // gets k hashes and sets relevant indices to true in bit
            bit[(int) (h % (long)m)] = true;
        }
    }

    // wrapper for string hashing
    public long hash(String s, long seed) {
        byte[] m = s.getBytes();
        return Murmur3.hash_x86_32(m, s.length(), seed);
    }

    public boolean contains(String s) {
        for(int i = 0; i < k; i++) {
            long h = hash(s, seeds[i]);
            if (bit[(int) (h % (long)m)] == false) { // if any index is false, return early
                return false;
            }
        }
        return true; // if all indices are true, return true
    }
    
    public static void main(String[] args) {
        bloomFilter bf;

        Scanner myObj = new Scanner(System.in);  // Create a Scanner object
        int numInputs = myObj.nextInt();
        int numChecks = myObj.nextInt();
        bf = new bloomFilter(numInputs);
        myObj.nextLine();

        // reads in and adds values to bloom filter
        for (int i = 0; i < numInputs; i++) {
            bf.add(myObj.nextLine());
        }

        int in = 0;

        // checks if test object is in the bloom filter
        for (int i = 0; i < numChecks; i++) {
            if (bf.contains(myObj.nextLine())) {
                in++;
            }
        }
        myObj.close();
        System.out.println("in: " + in);
        System.out.println("out: " + (numChecks - in));
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
             
 //			int k1 = (data[i4] & 0xff) + ((data[i4 + 1] & 0xff) << 8) + ((data[i4 + 2] & 0xff) << 16) + ((data[i4 + 3] & 0xff) << 24);
             
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
 
         // ----------
         // tail
 
         // Advance offset to the unprocessed tail of the data.
         
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
