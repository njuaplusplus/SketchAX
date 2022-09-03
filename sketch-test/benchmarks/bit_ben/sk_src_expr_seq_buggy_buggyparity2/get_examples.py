#!/usr/bin/env python
# coding=utf-8

import random


example_types = [
    ['bit_list_8'],
    ['bit'],
]

def parity(arr):
    return sum(arr)%2

def get_examples(num):
    W = 8
    examples = []
    while len(examples) < num:
        arr = [random.randint(0, 1) for _ in range(W)]
        examples.append(arr)
    return [
        [[arr], [parity(arr)]] for arr in examples
    ]
