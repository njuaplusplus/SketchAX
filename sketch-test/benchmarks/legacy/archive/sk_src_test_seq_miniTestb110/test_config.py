# coding=utf-8
import random

properties = [
    'permutation_invariant',
]

hard_properties = [
    'permutation_invariant',
]

W=5

examples = [
    ([[0,0,0,0,1]], [1]),
]
example_types = [
    ['bit_list_5'],
    ['bit'],
]

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0,1) for _ in range(W)]
        if not arr in examples:
            examples.append(arr)
    return [
        [[arr], [1]] for arr in examples
    ]

