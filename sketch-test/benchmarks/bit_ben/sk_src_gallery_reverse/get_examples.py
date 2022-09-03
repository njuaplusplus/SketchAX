#!/usr/bin/env python
# coding=utf-8
import random

example_types = [
    ['bit_list_32'],
    ['bit_list_32'],
]

def get_examples(num):
    W = 32
    examples = []
    while len(examples) < num:
        arr = [random.randint(0,1) for _ in range(W)]
        examples.append(arr)
    return [
        ([arr], [list(reversed(arr))]) for arr in examples
    ]
