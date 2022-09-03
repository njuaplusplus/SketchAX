# coding=utf-8
import numpy as np
import random

properties = [
]
hard_properties = [
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
    ['int', 'int', 'int',],
    ['int'],
]

def find(x,y,z):
    if 3*z >= 5:
        if 2*x <= y:
            return 3*x-5*y+7*z+9
        else:
            return 2*x-9*z+5
    else:
        if 2*z <= -y + 2*x:
            return -6*x + 3*y+4
        else:
            return 9*x+9*y-z+5


def get_examples(num):
    print('Using customized function to generate examples')
    examples = []
    while len(examples) < num:
        arr1 = [random.randint(0,10) for _ in range(N)]
        if not arr1 in examples:
            examples.append(arr1)
    return [
        ([x,y,z], [find(x,y,z)]) for x,y,z in examples
    ]
