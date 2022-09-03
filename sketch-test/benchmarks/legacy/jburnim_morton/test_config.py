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
    'permutation_permutation',
    'permutation_invariant',
    'k_rotation_invariant',
    'k_rotation_neg_k',
]
hard_properties = [
    'permutation_permutation',
]

times = 2
function_name = 'sketch1'
function_signatures = ['void sketch1',]
original_code_file = 'jburnim_morton_output.sk'
pbe_failed_sketch_file = 'jburnim_morton_pbe_failed.sk'
pbe_fixed_sketch_file = 'jburnim_morton_pbe_failed.sk'
examples = [
    [[[0,0,0,0,0,0,0,1],[0,0,0,0,0,0,0,0]],
     [[[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[1,0]]]],

    [[[1,1,1,1,1,1,0,0],[1,1,1,1,1,1,1,1]],
     [[[1,1],[1,1],[1,1],[1,1],[1,1],[1,1],[0,1],[0,1]]]],

    [[[0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,0]],
     [[[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,1],[0,0]]]],

    [[[1,1,1,1,1,1,0,0],[0,0,1,1,1,1,1,1]],
     [[[1,0],[1,0],[1,1],[1,1],[1,1],[1,1],[0,1],[0,1]]]],
]
example_types = [
    [list, list],
    [list],
]

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
