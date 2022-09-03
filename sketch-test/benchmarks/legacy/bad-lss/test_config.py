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
    'k_uniform_mult_k',
    'k_rotation_neg_k',
]
hard_properties = [
    'k_uniform_mult_k',
]

times = 1
function_name = 'lssSketch1'
function_signatures = ['void lssSketch1',]
original_code_file = 'lss_output.sk'
pbe_failed_sketch_file = 'lss_pbe_failed.sk'
pbe_fixed_sketch_file = 'lss_pbe_failed.sk'
W = 4
K = 20
# examples = [
#     ([[1,2,3,4]], [ 1]),
#     ([[4,5,6,7]], [10]),
#     ([[3,0,4,4]], [ 2]),
# ]
examples = [
    ([[-2,-1,0,1]], [ 1]),
    ([[1,2,3,4]], [10]),
    ([[0,-3,1,1]], [ 2]),
]
example_types = [
    [list],
    [int],
]

# def k_uniform_mult_lss(arr, k, maxsum):
#     maxsum *= k
#     arr = [k*x-3*(k-1) for x in arr]
#     print('assert lssSketch1({%s}) == %s;' %
#             (
#                 ','.join([str(x) for x in arr]),
#                 maxsum,
#             )
#     )
# 
# 
# def generate_examples_lss(k):
#     k_uniform_mult_lss([1,2,3,4], k, 1)
#     k_uniform_mult_lss([4,5,6,7], k, 10)
#     k_uniform_mult_lss([3,0,4,4], k, 2)
# 
def lss(arr):
    # arr = [ x - 3 for x in arr ]
    tmp_sum = 0
    maxsum = 0
    for i in range(W):
        tmp_sum = 0
        for j in range(i, W):
            tmp_sum += arr[j]
            if tmp_sum > maxsum:
                maxsum = tmp_sum
    return maxsum

def get_examples():
    examples = []
    while len(examples) < 3:
        arr = [random.randint(-8, 8) for _ in range(W)]
        if not arr in examples:
            examples.append(arr)
    return [
        ([arr], [lss(arr)]) for arr in examples
    ]


def generate_examples(examples):
    duplicate = []
    generated_examples = []

    for e_in, e_out in examples:
        for k in range(1,K):
            e_in_k = [k*x-3*(k-1) for x in e_in]
            e_out_k = k*e_out
            e_in_k_str = str(e_in_k)
            if e_in_k_str in duplicate:
                continue
            duplicate.append(e_in_k_str)
            generated_examples.append([e_in_k, e_out_k])
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

