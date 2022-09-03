# coding=utf-8
import random
import os
import sys
import importlib

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UTILS_DIR = os.path.join(ROOT_DIR, 'python')
sys.path.append(UTILS_DIR)
perturbation_model = 'perturbation'
perturbation = importlib.import_module(perturbation_model)
properties = [
    'permutation_invariant',
    # 'k_uniform_add_k',
    # 'k_uniform_mult_k',
    # 'k_rotation_invariant',
    # 'k_rotation_neg_k',
]
hard_properties = [
    'permutation_invariant',
]

times = 2
function_name = 'sum4RangeSK1'
function_signatures = ['void sum4RangeSK1',]
original_code_file = 'sum4Range_output.sk'
pbe_failed_sketch_file = 'sum4Range_pbe_failed.sk'
pbe_fixed_sketch_file = 'sum4Range_pbe_failed.sk'
W = 4
examples = [
# though right in hard constraints, wrong in soft constraints
#    ([[8,5,7,0], 4, 8], [12]),
#    ([[2,0,0,1], 0, 1], [ 0]),
#    ([[5,4,1,0], 1, 5], [ 4]),
     ([[5,3,4,1], 3, 7], [ 9]),
     ([[5,0,7,0], 4, 8], [12]),
     ([[5,1,2,6], 0, 2], [ 1]),
]
example_types = [
    [list, int, int],
    [int],
]

def sum4_range(arr, l, h):
    return sum([x for x in arr if l< x < h])

def get_examples():
    examples = []
    while len(examples) < 3:
        arr = [random.randint(0, 8) for _ in range(W)]
        if not arr in examples:
            l = random.randint(0, 4)
            h = l + random.randint(1, 4)
            examples.append((arr, l, h))
    return [
        [[arr, l, h], sum4_range(arr, l, h)] for arr,l,h in examples
    ]


def generate_examples(examples):
    duplicate = []
    generated_examples = []

    for (e_in, e_in_l, e_in_h), e_out in examples:
        e_in_str = str(e_in)
        if e_in_str in duplicate:
            continue
        for e_in_p in perm_unique(e_in):
            e_in_p_str = str(e_in_p)
            if e_in_p_str in duplicate:
                continue
            duplicate.append(e_in_p_str)
            generated_examples.append([[e_in_p, e_in_l, e_in_h], e_out])
    return generated_examples

def get_original_constraints_code(examples):
    return perturbation.get_hard_constraints_code_helper('original', function_name, example_types, examples)

def get_soft_constraints_code(examples):
    codes = ''
    for prop in properties:
        get_code =  getattr(perturbation, 'get_soft_constraints_%s_code' % prop, None)
        if get_code is not None:
            codes += get_code(function_name, example_types, examples)
        else:
            print('Function for property %s is undefined', prop)
    return codes

def get_hard_constraints_code(examples):
    codes = ''
    for prop in hard_properties:
        get_code =  getattr(perturbation, 'get_hard_constraints_%s_code' % prop, None)
        if get_code is not None:
            codes += get_code(function_name, example_types, examples)
        else:
            print('Hard constraints function for property %s is undefined' % prop)
    return codes
