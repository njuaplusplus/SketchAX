# coding=utf-8
import random

properties = [
    'permutation_invariant',
    'k_rotation_neg_k',
]
hard_properties = [
    'k_rotation_neg_k',
]

function_name = 'reverseSketch1'
function_signatures = ['void reverseSketch1',]
original_code_file = 'reverse_output.sk'
pbe_failed_sketch_file = 'reverse_pbe_failed.sk'
pbe_fixed_sketch_file = 'reverse_pbe_failed.sk'
W =8 
examples = [
    [
        [[1,0,0,0,0,0,0,1]],
        [[1,0,0,0,0,0,0,1]]
    ],
    [
        [[1,1,0,0,0,0,1,1]],
        [[1,1,0,0,0,0,1,1]]
    ],
    [
        [[1,0,1,0,0,1,0,1]],
        [[1,0,1,0,0,1,0,1]]
    ],
]
example_types = [
    ['bit_list_8'],
    ['bit_list_8'],
]

def get_examples():
    examples = []
    while len(examples) < 3:
        arr = [random.randint(0, 1) for _ in range(W)]
        if not arr in examples:
            examples.append(arr)
    return [
        [arr, list(reversed(arr))] for arr in examples
    ]

