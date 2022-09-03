# coding=utf-8
import random

properties = [
    'permutation_invariant',
    'k_rotation_neg_k',
]
hard_properties = [
    'permutation_invariant',
]

W=8

def logcount(x):
    return sum(x)

examples = [
    ([[1,1,0,0,0,0,0,0]], [[0,1,0,0,0,0,0,0]]),
    ([[1,1,1,1,0,0,0,0]], [[0,0,1,0,0,0,0,0]]),
    ([[1,1,1,0,0,0,0,0]], [[1,1,0,0,0,0,0,0]]),
]

example_types = [
    ['bit_list_8'],
    ['bit_list_8'],
]

def get_examples():
    examples = []
    while len(examples) < 3:
        x = [random.randint(0, 1) for _ in range(W)]
        if not x in examples:
            examples.append(x)
    return [
        [arr, logcount(arr)] for arr in examples
    ]

