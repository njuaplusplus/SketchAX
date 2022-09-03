# coding=utf-8
import numpy as np
import random

properties = [
]
hard_properties = [
    'not_permutation_invariant',
    'not_k_uniform_add_k',
    'not_k_uniform_mult_k',
]

# times = 1
# function_name = 'addSK1'
# function_signatures = ['void addSK1', ]
# original_code_file = 'arrayAdd_output.sk'
# pbe_failed_sketch_file = 'arrayAdd_pbe_failed.sk'
# pbe_fixed_sketch_file = 'arrayAdd_pbe_failed.sk'
N = 8


example_types = [
    ['int_list_%d' % N, 'int'],
    ['int'],
]

def get_examples(num):
    print('Using customized function to generate examples')
    examples = []
    while len(examples) < num:
        arr1 = [random.randint(0,5) for _ in range(N)]
        index = random.randint(0,10)
        if not [arr1, index] in examples:
            examples.append((arr1, index))
    return [
        ([arr1, index], [arr1[index] if index < N else -1]) for arr1, index in examples
    ]
