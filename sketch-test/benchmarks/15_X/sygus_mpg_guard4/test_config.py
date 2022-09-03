# coding=utf-8
import numpy as np
import random

properties = [
]
hard_properties = [
    'not_permutation_invariant',
    'not_k_uniform_add_k',
    'not_k_uniform_mult_k',
    'not_k_uniform_add_invariant',
    'not_k_uniform_mult_invariant',
]

# times = 1
# function_name = 'addSK1'
# function_signatures = ['void addSK1', ]
# original_code_file = 'arrayAdd_output.sk'
# pbe_failed_sketch_file = 'arrayAdd_pbe_failed.sk'
# pbe_fixed_sketch_file = 'arrayAdd_pbe_failed.sk'
N = 3


example_types = [
    ['int_list_%d' % N],
    ['int'],
]

def find(l):
    if l[0] + l[1] + sum(l) >= 1:
        return l[0]+l[1]
    else:
        return l[0]-l[1]

def get_examples(num):
    print('Using customized function to generate examples')
    examples = []
    while len(examples) < num:
        arr1 = [random.randint(0,10) for _ in range(N)]
        if not arr1 in examples:
            examples.append(arr1)
    return [
        ([arr1], [find(arr1)]) for arr1 in examples
    ]
