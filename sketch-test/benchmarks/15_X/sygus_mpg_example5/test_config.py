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
N = 2


example_types = [
    ['int', 'int'],
    ['int'],
]

def find(x, y):
    if x+y <= 1:
        return 10*(x+y+1)
    elif x+y <=2:
        return 20*(x+y-1)
    elif x+y<=3:
        return 30*(x+y+1)
    elif x+y <= 4:
        return 40*(x+y-1)
    elif x+y <= 5:
        return 50*(x+y+1)
    else:
        return 60*(x+y-1)


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
