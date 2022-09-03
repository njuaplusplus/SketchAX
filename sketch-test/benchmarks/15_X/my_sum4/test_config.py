# coding=utf-8
import random

# times = 1
# function_name = 'sumSK1'
# function_signatures = ['void sumSK1',]
# original_code_file = 'sum4_output.sk'
# pbe_failed_sketch_file = 'sum4_pbe_failed.sk'
# pbe_fixed_sketch_file = 'sum4_pbe_failed.sk'
W = 4
examples = [

    ([[5,1,3,6]], [15]),
    ([[2,8,0,10]], [20]),
    ([[0,7,10,7]], [24]),
]

example_types = [
    ['int_list_4'],
    ['int'],
]

properties = [
    'k_uniform_add_k',
    'k_uniform_mult_k',
    'permutation_invariant',
]

hard_properties = [
    'k_uniform_mult_k',
    'permutation_invariant',
    'not_k_uniform_add_k',
]

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0, 10) for _ in range(W)]
        if not arr in examples:
            examples.append(arr)
    return [
        [[arr], [sum(arr)]] for arr in examples
    ]

