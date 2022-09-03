# coding=utf-8
import random

# properties = [
#     'k_uniform_add_k',
#     'k_uniform_mult_k',
#     'permutation_invariant', # sufficient
# ]
hard_properties = [
    'k_uniform_add_k',
    'k_uniform_mult_k',
    'permutation_invariant', # sufficient
]

# times = 1
# function_name = 'maxSketch1'
# function_signatures = ['void maxSketch1',]
# original_code_file = 'max_output.sk'
# pbe_failed_sketch_file = 'max_pbe_failed.sk'
# pbe_fixed_sketch_file = 'max_pbe_failed.sk'

array_size = 2

example_types = [
    ['int_list_%d' % array_size],
    ['int'],
]
K = 10

T = 5
def sum25(x):
    for i in range(len(x)-1):
        if x[i]+x[i+1]>T:
            return x[i]+x[i+1]
    return 0

def get_examples(num):
    examples = []
    while len(examples) < num:
        size = array_size
        arr = [random.randint(0, 10) for _ in range(size)]
        if not arr in examples:
            examples.append(arr)
    return [
        ([arr], [sum25(arr)]) for arr in examples
    ]

