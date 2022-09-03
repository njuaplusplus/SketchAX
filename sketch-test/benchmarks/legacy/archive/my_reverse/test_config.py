# coding=utf-8
import random

properties = [
    'permutation_invariant',
    'k_rotation_invariant',
    'k_rotation_neg_k',
]

hard_properties = [
    'k_rotation_neg_k',
    'not_permutation_invariant',
    'not_permutation_permutation',
]

# times = 1
# function_name = 'reverseSketch1'
# function_signatures = ['void reverseSketch1',]
# original_code_file = 'reverse_output.sk'
# pbe_failed_sketch_file = 'reverse_pbe_failed.sk'
# pbe_fixed_sketch_file = 'reverse_pbe_failed.sk'
examples = [
    ([2,['a','b']], [['b','a']]),
    ([3,['a','b','a']], [['a','b','a']]),
    ([5,['a','b','b','a','a']], [['a','a','b','b','a']]),
    # ([5,['a','b','b','b','a']], [['a','b','b','b','a']]),
    # ([3,['b','b','b']], [['b','b','b']]),
    # ([6,['b','a','b','a','a','b']], [['b','a','a','b','a','b']]),
    # [[1, ['1']],             [['1']]],
    # [[2, ['1','1']],         [['1', '1']]],
    # [[3, ['1','2','1']],     [['1', '2', '1']]],
    # [[4, ['1','2','2','1']], [['1', '2', '2', '1']]],
]

example_types = [
    ['int_N', 'char_list_N'],
    ['char_list_N'],
]

def get_examples(num):
    examples = []
    while len(examples) < num:
#         size = random.randint(1,8)
#         arr = [random.choice(['a','b','c','d','e','f']) for _ in range(size)]
        size = random.randint(1,5)
        arr = [random.choice(['a','b','c', 'd']) for _ in range(size)]
        if not arr in examples:
            examples.append(arr)
    return [
        ([len(arr), arr], [list(reversed(arr))]) for arr in examples
    ]
