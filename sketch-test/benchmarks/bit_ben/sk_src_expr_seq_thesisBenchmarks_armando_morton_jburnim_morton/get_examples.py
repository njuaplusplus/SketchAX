#!/usr/bin/env python
# coding=utf-8

import random


example_types = [
    ['bit_list_8','bit_list_8',],
    ['bit_list_16',],
]


def interleave(x1, x2):
    assert len(x1) == len(x2)
    res = []
    for i in range(len(x1)):
        res.append(x1[i])
        res.append(x2[i])
    return res


def get_examples(num):
    W = 8
    examples = []
    while len(examples) < num:
        x1 = [random.randint(0, 1) for _ in range(W)]
        x2 = [random.randint(0, 1) for _ in range(W)]
        examples.append([x1,x2])
    return [
        [[x1,x2], [interleave(x1,x2)]] for x1,x2 in examples
    ]
