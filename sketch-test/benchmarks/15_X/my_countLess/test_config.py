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
# function_name = 'countLess1'
# function_signatures = ['void countLess1',]
# original_code_file = 'countLess_output.sk'
# pbe_failed_sketch_file = 'countLess_pbe_failed.sk'
# pbe_fixed_sketch_file = 'countLess_pbe_failed.sk'
W = 4
examples = [
    ([[1,7,6,0], 3], [2]),
    ([[6,7,8,6], 5], [0]),
    ([[4,2,8,3], 2], [0]),
]
example_types = [
    ['int_list_4', 'int'],
    ['int'],
]

def count_less(arr, v):
    return len([x for x in arr if x < v])

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0, 10) for _ in range(W)]
        if not arr in examples:
            examples.append((arr, random.randint(0, 10)))
    return [
        [[arr, v], [count_less(arr, v)]] for arr,v in examples
    ]

