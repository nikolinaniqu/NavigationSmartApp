def fib(n):
    sequence=[0,1]
    while len(sequence)<n:
       sequence.append(sequence[-1]+sequence[-2])
    return sequence[:]
print(fib(20))