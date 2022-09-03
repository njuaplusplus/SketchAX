# coding=utf-8
import numpy as np
import random

properties = [
]
hard_properties = [
    'not_permutation_invariant',
    'not_k_uniform_add_k',
    'k_uniform_mult_k',
]

# times = 1
# function_name = 'addSK1'
# function_signatures = ['void addSK1', ]
# original_code_file = 'arrayAdd_output.sk'
# pbe_failed_sketch_file = 'arrayAdd_pbe_failed.sk'
# pbe_fixed_sketch_file = 'arrayAdd_pbe_failed.sk'
N = 8


example_types = [
    ['int_list_%d' % N],
    ['int'],
]

def get_examples(num):
    print('Using customized function to generate examples')
    examples = []
    while len(examples) < num:
        arr1 = [random.randint(0,5) for _ in range(N)]
        if not arr1 in examples:
            examples.append(arr1)
    return [
        ([arr1,], [arr1[0] + arr1[3]]) for arr1 in examples
    ]
