# coding=utf-8
import numpy as np
import random

properties = [
    'permutation_permutation',
    'k1_k2_uniform_add_k1_k2',
    'k_uniform_add_k',
    'k_uniform_mult_k',
]
hard_properties = [
    'permutation_permutation', # eithor one can fix it
    'k_uniform_mult_k',
    # 'k1_k2_uniform_add_k1_k2',
    'not_permutation_invariant',
    'not_k_uniform_add_k',
    'not_k_rotation_neg_k',
]

# times = 1
# function_name = 'addSK1'
# function_signatures = ['void addSK1', ]
# original_code_file = 'arrayAdd_output.sk'
# pbe_failed_sketch_file = 'arrayAdd_pbe_failed.sk'
# pbe_fixed_sketch_file = 'arrayAdd_pbe_failed.sk'
N = 2

def arrayAdd(a1,a2):
    res = a1[:]
    for i, a in enumerate(res):
        res[i] += a2[i]
    return res

examples = [
    [[arr1, arr2], [arrayAdd(arr1,arr2)]] for arr1, arr2 in
        [
            #([2,1,1,0], [2,1,2,0]),
            #([1,0,1,0], [0,1,1,0]),
            #([0,1,2,2], [0,2,0,2]),
            ([2,1,1,0], [2,1,2,2]),
            ([1,0,1,0], [0,1,1,2]),
            ([0,1,2,2], [0,2,2,2]),
        ]
]
example_types = [
    ['int_list_4', 'int_list_4'],
    ['int_list_4'],
]

def get_examples(num):
    print('Using customized function to generate examples')
    examples = []
    while len(examples) < num:
        arr1 = [random.randint(0,10) for _ in range(4)]
        arr2 = [random.randint(0,10) for _ in range(4)]
        if not [arr1, arr2] in examples:
            examples.append([arr1, arr2])
    return [
        ([arr1, arr2], [arrayAdd(arr1, arr2)]) for arr1, arr2 in examples
    ]
