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
N = 4


example_types = [
    ['int', 'int', 'int', 'int'],
    ['int'],
]

def find(x,y,z,z1):
    if 2*x+ z - z1 >= -y:
        if x + z1 <= y:
            return 10*x + 20*y + 15*z - 99
        else:
            return 9*y + 25*z1 - 11
    else:
        if x + 3*z + z1 <= -9:
            return 11*x + 15*y + 30*z + 22*z1 + 11
        else:
            return 16*x + 18*z + 5*z1  - 55


def get_examples(num):
    print('Using customized function to generate examples')
    examples = []
    while len(examples) < num:
        arr1 = [random.randint(0,10) for _ in range(N)]
        if not arr1 in examples:
            examples.append(arr1)
    return [
        ([*arr1], [find(*arr1)]) for arr1 in examples
    ]
