#!/usr/bin/env python
# coding=utf-8

import random


example_types = [
    ['bit_list_8',],
    ['bit_list_8',],
]


def logcount(x):
    return sum(x)


def get_examples(num):
    W = 4
    examples = []
    while len(examples) < num:
        x = [random.randint(0, 1) for _ in range(W)]
        examples.append(x)
    return [
        [[arr], [list(reversed(bin(logcount(arr))[2:].rjust(W,'0')))]] for arr in examples
    ]
