# coding=utf-8
import random

properties = [
    'permutation_invariant',
    'k_rotation_invariant',
    'k_rotation_neg_k',
]
hard_properties = [
    'permutation_invariant',
]

W=8
examples = [
        ([[1,0,1,0,1,1,1,1]], [0]),
        ([[1,0,1,1,0,1,0,0]], [0]),
        ([[1,0,1,1,0,0,1,0]], [0]),
        ([[0,1,0,0,1,1,0,0]], [1]),
        ([[0,1,1,0,1,0,0,0]], [1]),
]
example_types = [
    ['bit_list_8'],
    ['bit'],
]

def parity(arr):
    return sum(arr)%2

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0, 1) for _ in range(W)]
        if not arr in examples:
            examples.append(arr)
    return [
        [[arr], [parity(arr)]] for arr in examples
    ]

