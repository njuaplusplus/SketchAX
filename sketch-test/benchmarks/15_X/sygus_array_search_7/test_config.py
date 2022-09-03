# coding=utf-8
import numpy as np
import random

properties = [
]
hard_properties = [
    'not_permutation_invariant',
    'not_k_uniform_add_k',
    'not_k_uniform_mult_k',
    'k_uniform_add_invariant',
    'k_uniform_mult_invariant',
]

# times = 1
# function_name = 'addSK1'
# function_signatures = ['void addSK1', ]
# original_code_file = 'arrayAdd_output.sk'
# pbe_failed_sketch_file = 'arrayAdd_pbe_failed.sk'
# pbe_fixed_sketch_file = 'arrayAdd_pbe_failed.sk'
N = 7


example_types = [
    ['int_list_%d' % N, 'int'],
    ['int'],
]

def find(l, k):
    l_sorted = sorted(l)
    for i in range(len(l)):
        if l[i] != l_sorted[i]:
            return 0
    i = 0
    for v in l:
        if k < v: return i
        i += 1
    return i

def get_examples(num):
    print('Using customized function to generate examples')
    examples = []
    choices = list(range(0,10))
    while len(examples) < num:
        arr1 = random.sample(choices, N)
        if random.randint(0,9)%2 == 0:
            arr1.sort()
        k = random.randint(0,10)
        if not [arr1, k] in examples:
            examples.append([arr1,k])
    return [
        ([arr1, k], [find(arr1, k)]) for arr1,k in examples
    ]
