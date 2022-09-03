# coding=utf-8
import random

properties = [
    'permutation_invariant',
    'k_uniform_add_k',
    'k_uniform_mult_k',
]
hard_properties = [
    'permutation_invariant', # sufficient
    'k_uniform_add_k',
    'k_uniform_mult_k',
]

# times = 1
# function_name = 'maxSketch1'
# function_signatures = ['void maxSketch1',]
# original_code_file = 'max_output.sk'
# pbe_failed_sketch_file = 'max_pbe_failed.sk'
# pbe_fixed_sketch_file = 'max_pbe_failed.sk'
examples = [
   ([1, [-1]], [-1]),
   ([3, [ 0,10, 2]], [10]),
   ([3, [-1,10,20]], [20]),
   ([3, [-1,-2,-3]], [-1]),
]

example_types = [
    ['int_N', 'int_list_N',],
    ['int'],
]

def get_examples(num):
    examples = []
    while len(examples) < num:
        size = random.randint(3,5)
        arr = [random.randint(0, 10) for _ in range(size)]
        if not arr in examples:
            examples.append(arr)
    return [
        ([len(arr), arr], [max(arr)]) for arr in examples
    ]

