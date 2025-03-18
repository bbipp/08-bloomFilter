import math
import mmh3

x = 1
y = x.to_bytes(math.ceil(x.bit_length() / 8), "big")
print (mmh3.mmh3_32_uintdigest(y, 2538058380))