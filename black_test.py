import itertools


def iter_primes():
    # an iterator of all numbers between 2 and +infinity
    numbers = itertools.count(2)

    # generate primes forever
    while True:
        # get the first number from the iterator (always a prime)
        prime = next(numbers)
        yield prime
        # this code iteratively builds up a chain of
        # filters...slightly tricky, but ponder it a bit
        numbers = filter(prime.__rmod__, numbers)


if __name__ == "__main__":
    print("print all primes < 400")
    for p in iter_primes():
        if p > 400:
            break
        print(p)
