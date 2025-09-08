import math
from math import factorial

print(dir(math))
print(dir(factorial))
help(dict)

import math

for name in dir(math):
    print(name, end="\t")

