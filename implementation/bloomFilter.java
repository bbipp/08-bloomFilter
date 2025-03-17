class bloomFilter {
    // number of hashing functions
    private int k;

    // size of BIT array
    private int m;

    // expected number of elements to be added
    private int n;

    // calculates the probability of false positive
    public int getProb() {
        return((int)Math.pow(1 - Math.pow((1 - (1 / m)), k * n), k));
    }

    public void setN(int n) {
        this.n = n;
    }

    // sets m to guarantee a probability P on n inputs
    public void setMByP(float P) {
        this.m = (int)-((n * Math.log(P)) / Math.pow(Math.log(2), 2));
    }

    // sets m to any integer
    public void setM(int m) {
        this.m = m;
    }
    
    public static void main(String[] args) {

    }
}
