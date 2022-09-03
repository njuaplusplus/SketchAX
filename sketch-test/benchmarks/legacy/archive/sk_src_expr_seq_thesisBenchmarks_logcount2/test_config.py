# coding=utf-8
import random

properties = [
    'permutation_invariant',
    'k_rotation_neg_k',
]
hard_properties = [
    'permutation_invariant',
]

def logcount(x):
    return sum(x)

examples = [
    ([[1,1,0,0,0,0,0,0]], [[0,1,0,0,0,0,0,0]]),
    ([[1,1,1,1,0,0,0,0]], [[0,0,1,0,0,0,0,0]]),
    ([[1,1,1,0,0,0,0,0]], [[1,1,0,0,0,0,0,0]]),
#    ([[1,1,0,0,0,0,1,0]], [[1,1,0,0,0,0,0,0]]),
#    ([[1,0,1,0,0,0,1,0]], [[1,1,0,0,0,0,0,0]]),
#    ([[0,0,1,0,1,0,1,1]], [[0,0,1,0,0,0,0,0]]),
]

example_types = [
    ['bit_list_8'],
    ['bit_list_8'],
]

W = 8
def logcount(x):
    return sum(x)

def get_examples(num):
    examples = []
    while len(examples) < num:
        x = [random.randint(0, 1) for _ in range(W)]
        if not x in examples:
            examples.append(x)
    return [
        [[arr], [list(reversed(bin(logcount(arr))[2:].rjust(8,'0')))]] for arr in examples
    ]

