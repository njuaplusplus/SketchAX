#!/usr/bin/env python
# coding=utf-8

import random


example_types = [
    ['bit_list_4',],
    ['bit_list_4',],
]


def get_examples(num):
    W = 4
    examples = []
    while len(examples) < num:
        x = [random.randint(0, 1) for _ in range(W)]
        examples.append(x)
    return [
        [[arr], [arr]] for arr in examples
    ]
