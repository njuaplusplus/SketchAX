# coding=utf-8
import numpy as np

properties = [
    'k_uniform_add_k',
    'k_uniform_mult_k',
    'row_permutation_col_permutation',
]
hard_properties = [
    'k_uniform_add_k',
    'k_uniform_mult_k',
    'row_permutation_col_permutation', # sufficient
]

N = 4
K = 2
examples = [
#     # This two examples were randomly generated
#     ( [np.array([
#         [ 7, 6, 5, 6],
#         [ 3, 6, 2,10],
#         [ 2, 7, 0, 0],
#         [10,10, 2,10]
#       ])],
#       [np.array([
#         [ 7, 3, 2,10],
#         [ 6, 6, 7,10],
#         [ 5, 2, 0, 2],
#         [ 6,10, 0,10]
#       ])]
#     ),
#     ( [np.array([
#         [ 6, 6, 2, 8],
#         [ 6,10, 5, 5],
#         [ 4, 4, 3, 1],
#         [ 1, 3,10, 3]
#       ])],
#       [np.array([
#         [ 6, 6, 4, 1],
#         [ 6,10, 4, 3],
#         [ 2, 5, 3,10],
#         [ 8, 5, 1, 3]
#       ])]
#     ),
    [[x], [x.transpose()]] for x in
        [
            np.array([
                [0,0,1,0],
                [1,0,1,0],
                [1,4,0,0],
                [1,0,1,0],
            ]),
            np.array([
                [0,0,1,2],
                [0,0,1,0],
                [1,1,0,0],
                [1,0,2,0],
            ]),
            np.array([
                [1,0,1,0],
                [1,0,1,3],
                [1,2,3,0],
                [1,0,1,0],
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
