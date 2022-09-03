# coding=utf-8
import random

properties = [
    'k_uniform_add_k',
    'k_uniform_mult_k',
    'permutation_invariant', # sufficient
]
hard_properties = [
    'k_uniform_add_k',
    'k_uniform_mult_k',
    'permutation_invariant', # sufficient
    'not_k_uniform_add_invariant',
    'not_k_uniform_mult_invariant',
]

# times = 1
# function_name = 'maxSketch1'
# function_signatures = ['void maxSketch1',]
# original_code_file = 'max_output.sk'
# pbe_failed_sketch_file = 'max_pbe_failed.sk'
# pbe_fixed_sketch_file = 'max_pbe_failed.sk'
examples = [
        ([[8,5, 9]], [ 9]),
        ([[6,5, 0]], [ 6]),
        ([[0,0,10]], [10]),
        ([[6,2,10]], [10]),
        ([[1,1, 4]], [ 4]),
#     ([[ 0,10, 2]], [10]),
#     ([[-1,10,20]], [20]),
#     ([[-1,-2,-3]], [-1]),
#     ([[1,2,3]], [3]),
#     ([[3,4,5]], [5]),
#     ([[5,6,7]], [7]),
]

N = 3
example_types = [
    ['int_list_%d' % N],
    ['int'],
]
K = 10

def get_examples(num):
    examples = []
    while len(examples) < num:
        arr = [random.randint(0, 10) for _ in range(N)]
        if not arr in examples:
            examples.append(arr)
    return [
        ([arr], [max(arr)]) for arr in examples
    ]

