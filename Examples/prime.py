#!/usr/bin/env python3

import sys
import ray

def usage(argv0):
    print("usage: {} <max number>".format(argv0))
    print("")
    print("will list all prime number up to max number")
    print("")

def num_bits(x):
    '''
    how much bits are used to store x (assumed to be an integer)
    '''

    bits = 0

    while x > 0:
        x >>= 1
        bits += 1

    return bits


def quick_sqrt(x):
    '''
    efficiently calculate a approxmitative majorant sqrt(x)
    (assuming x to be an integer)
    this function is only valid for x > 3
    '''

    bits = num_bits(x)
    shift = bits // 2
    rest = bits % 2
    if rest > 0:
        shift += 1
    maj = 1 << shift

    # maj contains the lower weight half bits set to 1
    # if the number of bits is not divisible by 2 this
    # is one bit more that is set to one.

    if maj > x:
        maj = x

    return maj



@ray.remote(num_cpus=1)
def prime(x):
    '''
    return x if x is prime, else 0 is returned
    '''
    div = 2
    cmax = quick_sqrt(x)
    not_prime = False
    while div < cmax and not not_prime:
        if x % div == 0:
            not_prime = True
        div += 1

    if not_prime:
        return 0
    else:
        return x


def action(maxval):
    ray.init()

    x = 2
    tret = []
    while x < maxval:
        tret.append(prime.remote(x))
        x += 1

    res = []
    for x in tret:
        val = ray.get(x)
        if val != 0:
            res.append(val)
    print(res)

    ray.shutdown()



if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage(sys.argv[0])
    else:
        action(int(sys.argv[1]))
