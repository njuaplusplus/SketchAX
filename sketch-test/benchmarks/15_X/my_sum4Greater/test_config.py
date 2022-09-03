# coding=utf-8
import random

# times = 1
# function_name = 'sumGreaterSK1'
# function_signatures = ['void sumGreaterSK1',]
# original_code_file = 'sum4Greater_output.sk'
# pbe_failed_sketch_file = 'sum4Greater_pbe_failed.sk'
# pbe_fixed_sketch_file = 'sum4Greater_pbe_failed.sk'
W = 4
examples = [
    ([[5,6,0,3], 1],  [14]),
    ([[5,7,6,5], 8],  [ 0]),
    ([[1,0,1,5], 5],  [ 0]),
]
example_types = [
    ['int_list_4', 'int'],
    ['int'],
]

properties = [
    'permutation_invariant',
    'k_uniform_add_k',
    'k_uniform_mult_k',
]

hard_properties = [
    'k_uniform_mult_k',
    'permutation_invariant', # sufficient
    'not_k_uniform_add_k',
]

def sum_greater(arr, v):
    return sum([x for x in arr if x > v])

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0, 10) for _ in range(W)]
        if not arr in examples:
            examples.append((arr, random.randint(0, 10)))
    return [
        [[arr,v], [sum_greater(arr, v)]] for arr,v in examples
    ]

