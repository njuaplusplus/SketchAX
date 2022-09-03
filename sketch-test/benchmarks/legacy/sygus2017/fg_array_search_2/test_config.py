# coding=utf-8
import random

# properties = [
#     'k_uniform_add_k',
#     'k_uniform_mult_k',
#     'permutation_invariant', # sufficient
# ]
hard_properties = [
    'k_uniform_add_invariant',
    'k_uniform_mult_invariant',
]

# times = 1
# function_name = 'maxSketch1'
# function_signatures = ['void maxSketch1',]
# original_code_file = 'max_output.sk'
# pbe_failed_sketch_file = 'max_pbe_failed.sk'
# pbe_fixed_sketch_file = 'max_pbe_failed.sk'

array_size = 2

example_types = [
    ['int_list_%d' % array_size, 'int'],
    ['int'],
]
K = 10

def search2(l, k):
    i = 0
    for x in l:
        if x < k:
            i += 1
        else:
            break
    return i

def get_examples(num):
    examples = []
    while len(examples) < num:
        size = array_size
        arr = sorted([random.randint(0, 10) for _ in range(size)])
        dup = False
        for i in range(array_size-1):
            if arr[i] == arr[i+1]:
                dup = True
                break
        if dup:
            continue
        if not arr in examples:
            examples.append([arr, random.randint(0, 10)])
    return [
        ([arr, k], [search2(arr,k)]) for arr,k in examples
    ]

