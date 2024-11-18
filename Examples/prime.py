#!/usr/bin/env python3

########################################################################
# translate.py - a simple script to install Ray on Linux
# Copyright (C) 2024 Denis Corbin
#
#  translate.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  translate.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Webdar.  If not, see <http://www.gnu.org/licenses/>
#
########################################################################

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
