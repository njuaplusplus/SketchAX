# coding=utf-8
import random

properties = [
    'permutation_invariant',
    'k_uniform_add_k',
    'k_uniform_mult_k',
    'k_rotation_invariant',
    'k_rotation_neg_k',
]
hard_properties = [
    'permutation_invariant',
    'not_k_uniform_add_k',
    'not_k_uniform_mult_k',
]

# times = 1
# function_name = 'countRange1'
# function_signatures = ['void countRange1',]
# original_code_file = 'countRange_output.sk'
# pbe_failed_sketch_file = 'countRange_pbe_failed.sk'
# pbe_fixed_sketch_file = 'countRange_pbe_failed.sk'
W = 4
examples = [
    ([[8,5,7,0], 4, 8], [2]),
    ([[2,0,0,1], 0, 1], [0]),
    ([[5,4,1,0], 1, 5], [1]),
]

example_types = [
    ['int_list_4', 'int', 'int'],
    ['int'],
]

def count_range(arr, l, h):
    return len([x for x in arr if l< x < h])

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0, 10) for _ in range(W)]
        if not arr in examples:
            l = random.randint(0, 5)
            h = l + random.randint(1, 5)
            examples.append((arr, l, h))
    return [
        [[arr, l, h], [count_range(arr, l, h)]] for arr,l,h in examples
    ]
