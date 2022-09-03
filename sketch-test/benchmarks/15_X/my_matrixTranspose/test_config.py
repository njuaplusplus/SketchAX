# coding=utf-8
import numpy as np
import random

properties = [
    'k_uniform_add_k',
    'row_permutation_col_permutation',
]
hard_properties = [
    'k_uniform_add_k', # this property alone cannot fix the problem.
    'k_uniform_mult_k', # this property alone cannot fix the problem.
    'row_permutation_col_permutation',
]

# times = 1
# function_name = 'transposeSK1'
# function_signatures = ['void transposeSK1', ]
# original_code_file = 'matrixTranspose_output.sk'
# pbe_failed_sketch_file = 'matrixTranspose_pbe_failed.sk'
# pbe_fixed_sketch_file = 'matrixTranspose_pbe_failed.sk'
N = 3

examples = [
    [[arr1], [arr1.transpose()]] for arr1 in
        [
            np.array([[2,1,0],[1,0,0],[0,1,0]]),
            np.array([[1,0,0],[1,0,0],[1,0,1]]),
            np.array([[0,1,0],[2,2,0],[2,0,1]]),
        ]
]
example_types = [
    ['matrix'],
    ['matrix'],
]

def get_examples(num):
    examples = []
    tmp = []
    while len(examples) < num:
        arr = np.random.random_integers(0, 10, (N, N))
        m_str = list(arr.flatten())
        if not m_str in tmp:
            examples.append(arr)
            tmp.append(m_str)
    return [
        [[arr], [arr.transpose()]] for arr in examples
    ]

