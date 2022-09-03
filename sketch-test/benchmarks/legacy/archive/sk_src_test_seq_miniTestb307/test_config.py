# coding=utf-8
import random

properties = [
    'k_rotation_invariant',
    'k_rotation_neg_k',
]

hard_properties = [
    'k_rotation_neg_k',
]

examples = [
    ([[0,0,0,0,1,1,1,1,1,0,1,1,0,1,0,0]],[[0,0,1,0,1,1,0,1,1,1,1,1,0,0,0,0]]),
    ([[0,0,1,1,0,1,0,1,0,0,0,0,0,0,0,1]],[[1,0,0,0,0,0,0,0,1,0,1,0,1,1,0,0]]),
    ([[0,1,0,1,0,0,1,0,1,1,1,1,1,1,1,1]],[[1,1,1,1,1,1,1,1,0,1,0,0,1,0,1,0]]),
]

example_types = [
    ['bit_list_16'],
    ['bit_list_16'],
]

W = 16

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0,1) for _ in range(W)]
        if not arr in examples:
            examples.append(arr)
    return [
        ([arr], [list(reversed(arr))]) for arr in examples
    ]
