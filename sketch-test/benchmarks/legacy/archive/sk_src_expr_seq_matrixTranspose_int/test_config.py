# coding=utf-8
import numpy as np

properties = [
    'k_uniform_add_k',
    # 'row_permutation_col_permutation', too slow
]
hard_properties = [
    'k_uniform_add_k', # sufficient
    'k_uniform_mult_k',
    'row_permutation_col_permutation', # too slow
]

# times = 1
# function_name = 'tiledTranspose1'
# function_signatures = ['void tiledTranspose1', ]
# original_code_file = 'matrixTranspose_output.sk'
# pbe_failed_sketch_file = 'matrixTranspose_pbe_failed.sk'
# pbe_fixed_sketch_file = 'matrixTranspose_pbe_fixed.sk'
N = 10
K = 2
examples = [
    [[x], [x.transpose()]] for x in
        [
            np.array([
                [0,0,1,0,1,0,1,0,1,0],
                [1,0,1,0,1,0,1,0,1,0],
                [1,0,0,0,1,0,1,0,1,0],
                [1,0,1,0,1,0,1,0,1,0],
                [1,0,1,0,0,0,1,0,1,0],
                [1,0,1,0,1,0,1,0,1,0],
                [1,0,1,0,1,0,0,0,1,0],
                [1,0,1,0,1,0,1,0,1,0],
                [1,0,1,0,1,0,1,0,0,0],
                [1,0,1,0,1,0,1,0,1,0],
            ]),
            np.array([
                [0,0,1,0,1,0,1,0,1,0],
                [1,0,2,0,1,0,1,0,1,0],
                [1,0,0,0,1,0,2,0,1,0],
                [1,0,1,0,1,0,1,0,1,0],
                [1,0,1,0,0,0,1,0,1,0],
                [2,0,1,0,1,0,1,0,1,0],
                [1,0,1,0,1,0,0,2,1,0],
                [1,0,1,0,1,0,1,0,1,0],
                [1,0,1,0,2,0,1,0,0,0],
                [1,0,1,0,1,0,1,0,2,0],
            ]),
            np.array([
                [0,0,1,0,1,0,1,0,1,0],
                [1,0,3,0,1,0,3,0,1,0],
                [1,0,0,0,1,0,1,0,1,0],
                [1,0,3,0,1,0,1,3,1,0],
                [1,0,1,0,0,0,3,0,3,0],
                [1,0,1,3,1,0,3,0,1,0],
                [1,0,3,0,3,0,0,0,1,0],
                [1,0,1,0,1,0,1,3,1,0],
                [1,0,1,0,3,0,3,0,0,0],
                [1,0,3,0,1,0,1,0,1,0],
            ]),
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
