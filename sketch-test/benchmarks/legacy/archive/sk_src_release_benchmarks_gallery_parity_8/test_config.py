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

# times = 1
# function_name = 'fastparity1'
# function_signatures = ['void fastparity1',]
# original_code_file = 'parity_output.sk'
# pbe_failed_sketch_file = 'parity_pbe_failed.sk'
# pbe_fixed_sketch_file = 'parity_pbe_failed.sk'
W=8
examples = [
    ([[0,0,0,0,0,0,0,0]], [0]),
    ([[1,0,0,0,0,0,0,0]], [1]),
    ([[1,1,0,0,0,0,0,0]], [0]),
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

