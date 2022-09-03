# coding=utf-8
import numpy as np
import random

properties = [
    'permutation_permutation',
    'k1_k2_uniform_add_k1_k2',
    'k_uniform_add_k',
    'row_permutation_col_permutation',
]
hard_properties = [
    'permutation_permutation', # only this is sufficient
    'k_uniform_mult_k',
    # 'k_uniform_add_2k', # try k1_k2_uniform_add_k1+k2
    # 'k1_k2_uniform_add_k1_k2', # only this is sufficient
    'not_permutation_invariant',
    'not_k_uniform_add_k',
    'not_k_rotation_neg_k',
]

# times = 1
# function_name = 'addSK1'
# function_signatures = ['void addSK1', ]
# original_code_file = 'matrixAdd_output.sk'
# pbe_failed_sketch_file = 'matrixAdd_pbe_failed.sk'
# pbe_fixed_sketch_file = 'matrixAdd_pbe_failed.sk'
N = 2

examples = [
    [[arr1, arr2], [arr1+arr2]] for arr1, arr2 in
        [
            [np.array([[2,1],[1,0]]), np.array([[2,1],[2,2]])],
            [np.array([[1,0],[1,0]]), np.array([[0,1],[1,2]])],
            [np.array([[0,1],[2,2]]), np.array([[0,2],[2,2]])],
        ]
]
example_types = [
    ['int_matrix_2_2', 'int_matrix_2_2'],
    ['int_matrix_2_2'],
]

def get_examples(num):
    examples = []
    tmp = []
    while len(examples) < num:
        arr1 = np.random.random_integers(0, 10, (N, N))
        arr2 = np.random.random_integers(0, 10, (N, N))
        m_str = list(arr1.flatten()) + list(arr2.flatten())
        if not m_str in tmp:
            examples.append((arr1, arr2))
            tmp.append(m_str)
    return [
        [[arr1, arr2], [arr1+arr2]] for arr1,arr2 in examples
    ]

