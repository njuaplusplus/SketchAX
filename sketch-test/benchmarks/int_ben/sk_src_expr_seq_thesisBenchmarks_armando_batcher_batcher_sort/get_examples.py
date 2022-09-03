#!/usr/bin/env python
# coding=utf-8

import random


example_types = [
    ['int_list_4',],
    ['int',],
]


def logcount(x):
    return sum(x)


def get_examples(num):
    W = 4
    examples = []
    while len(examples) < num:
        x = [random.randint(0, 10) for _ in range(W)]
        examples.append(x)
    return [
        [[arr], [0,]] for arr in examples
    ]
