#!/usr/bin/env python3
# coding=utf-8

import subprocess
from shutil import copyfile, rmtree
import datetime
import os
import sys
import importlib
import re
import glob
import perturbation
import random
import signal
import argparse
import time
import string
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

BENCHMARKS_DIR = os.path.join(BASE_DIR, 'benchmarks')
ARGS_DIR = ['benchmarks',]

TIMING = False

TIME_LIMIT_FOR_CONSTRAINTS = 5 # seconds
EXAMPLE_BOUND = -5 # for 10 seconds
NUMS_OF_EXAMPLES = [3]

USE_RANDOM_EXAMPLES = False
BRUTE_PRESET_EXAMPLES = None
BRUTE_NEED_REMEMBER_EXAMPLES = False

JUST_GEN_RAND_EXAMPLE = False
LOAD_EXAMPLE_FROM_FILE = False
FIXED_EXAMPLES_FILE = 'fixed_examples.txt'
REPEAT_INDEX = 0

ENFORCEMENT_STRATEGY = 'disjunction'
INFERENCE_STRATEGY = 'disjunction'

USE_DEFAULT_RAW_SKETCH = False
USE_RANKING_STRATEGY = False

PERTURBATION_PROPERTIES = perturbation.PROPERTIES
INTERACTIVE_LEVEL = 0
USE_SPEC_AS_USER = False
INFER_NEG_PROP_BY_POS_PROP = False
INVERT_ONE_POSITIVE_PROP = False

NUM_OF_POSITIVE_EXAMPLES_TO_SHOW = 1
NUM_OF_NEGATIVE_EXAMPLES_TO_SHOW = 1

BENCHMARK_PROPERTY_DICT = None
LOAD_PROPERTIES = False
ONLY_USE_POSITIVE_PROPERTIES = False

ONLY_COUNTING_NUM_OF_EXAMPLES = False
BEN_NUM_OF_EXAMPLES_DICT = {}
BEN_NUM_OF_POS_EXAMPLES_DICT = {}
BEN_NUM_OF_NEG_EXAMPLES_DICT = {}

USE_OWN_GENERATOR = False
OWN_GENERATED_EXAMPLES_FILE = 'own_examples.txt'

def load_ben_prop_dict():
    prop_file = os.path.join(BENCHMARKS_DIR, 'properties.conf')
    if not os.path.isfile(prop_file):
        print('properties.conf does not exist')
        return None
    ben_prop_dict = {}
    lines = []
    with open(prop_file) as in_file:
        for l in in_file:
            lines.append(l.strip().split('\t'))

    for l in lines:
        tmp = [x.strip() for x in l[1].split(',')]
        if ONLY_USE_POSITIVE_PROPERTIES:
            tmp = [x for x in tmp if not x.startswith('not')]
        tmp.sort()
        ben_prop_dict[l[0]] = tmp
    return ben_prop_dict

def save_examples(filename, example_types, examples):
    def str_matrix(mat):
        mat = [','.join([str(x) for x in row]) for row in mat]
        return '{{%s}}' % '},{'.join(mat)

    def str_inputs(input_types, inputs):
        res = []
        for i,e_in in enumerate(inputs):
            if input_types[i] == 'int' or input_types[i] == 'bit' or input_types[i] == int:
                res.append(str(e_in))
            elif input_types[i] == list or 'list' in input_types[i]:
                if isinstance(e_in[0], (list, tuple)):
                    res.append(
                        '{%s}' % ','.join([','.join([str(x) for x in t]) for t in e_in])
                    )
                else:
                    if 'char' in input_types[i]:
                        res.append("{'%s'}" % "','".join(e_in))
                    else:
                        res.append(
                            '{%s}' % ','.join([str(x) for x in e_in])
                        )
            elif 'matrix' in input_types[i]:
                res.append(str_matrix(e_in))
            else:
                # TODO: brute fix for int_N
                res.append(str(e_in))
        return ' | '.join(res)

    with open(filename, 'a') as out_file:
        out_file.write('======= Begin Example ======\n')
        out_file.write(','.join(example_types[0]))
        out_file.write('\n')
        out_file.write(','.join(example_types[1]))
        out_file.write('\n')
        for example in examples:
            out_file.write(str_inputs(example_types[0], example[0])),
            out_file.write(' => ')
            out_file.write(str_inputs(example_types[1], example[1])),
            out_file.write('\n')
        out_file.write('======= End Example ======\n')


def load_example_wrapper(filename, index, num_of_exams=3):
    if num_of_exams <= 3:
        example_types, examples = load_example(filename, index)
        return example_types, examples[:num_of_exams]
    else:
        example_types, examples = load_example(filename, index)
        examples.extend(load_example(filename, (index+1)%10)[1][:(num_of_exams-3)])
        return example_types, examples


def load_example(filename, index, num_of_exams=3):
    """ Load the ith example set from a file
    """
    cur = -1
    lines = []
    example_types = []
    examples = []
    with open(filename) as in_file:
        for l in in_file:
            lines.append(l.strip())

    for row in range(0, len(lines), 4+num_of_exams):
        line = lines[row]
        if line.startswith('======= Begin'):
            cur += 1
        if cur == index:
            e_in_type = lines[row+1].split(',')
            e_out_type = lines[row+2].split(',')
            example_types = [e_in_type, e_out_type]
            for i in range(num_of_exams):
                line = lines[row+3+i]
                e_ins_str, e_out_str = line.split(' => ')
                e_in_strs = e_ins_str.split(' | ')
                e_ins = []
                for ii, e_in_s in enumerate(e_in_strs):
                    if e_in_type[ii] == 'int' or e_in_type[ii] == 'bit' or e_in_type[ii] == 'int_N':
                        e_ins.append(int(e_in_s))
                    elif 'list' in e_in_type[ii]:
                        if 'char' in e_in_type[ii]:
                            e_ins.append([x.strip()[1:-1] for x in e_in_s[1:-1].split(',')])
                        else:
                            e_ins.append([int(x) for x in e_in_s[1:-1].split(',')])
                    elif 'matrix' in e_in_type[ii]:
                        t_rows = e_in_s[2:-2].split('},{')
                        t_rows = [ [int(x) for x in r.split(',')] for r in t_rows ]
                        e_ins.append(np.array(t_rows))
                if e_out_type[0] == 'int' or e_out_type[0] == 'bit':
                    e_out = int(e_out_str)
                elif 'list' in e_out_type[0]:
                    if 'char' in e_out_type[0]:
                        e_out = [x.strip()[1:-1] for x in e_out_str[1:-1].split(',')]
                    else:
                        e_out = [int(x) for x in e_out_str[1:-1].split(',')]
                elif 'matrix' in e_out_type[0]:
                    t_rows = e_out_str[2:-2].split('},{')
                    t_rows = [ [int(x) for x in r.split(',')] for r in t_rows ]
                    e_out = np.array(t_rows)
                examples.append([e_ins, [e_out]])
            break
    return example_types, examples


def get_time():
    return time.perf_counter()
    # return time.process_time()

def timeout_handler(signum, frame):
    raise Exception('Timeout for %ds!' % TIME_LIMIT_FOR_CONSTRAINTS)

def get_original_constraints_code(function_name, example_types, examples):
    return perturbation.get_hard_constraints_code_helper('original', function_name, example_types, examples)[0]

def get_soft_constraints_code(properties, function_name, example_types, examples, y_percent=-1, need_generation=True):
    def helper(bound=0):
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(TIME_LIMIT_FOR_CONSTRAINTS)
        codes = ''
        examples_list = []
        for prop in properties:
            tmp = perturbation.get_soft_constraints_code_helper(prop, function_name, example_types, examples, bound=bound, y_percent=y_percent, need_generation=need_generation)
            codes += tmp[0]
            examples_list.append(tmp[1])
        # signal.alarm(0)
        return codes, examples_list

    return helper(EXAMPLE_BOUND)

    # codes = ''
    # try:
    #     codes = helper()
    # except Exception as err:
    #     print('Generating soft constraints of %s has error: %s\nTry to generate with bounds %s' % (properties,err,EXAMPLE_BOUND))
    #     codes = helper(EXAMPLE_BOUND)
    # return codes


def get_hard_constraints_code(hard_properties, function_name, example_types, examples, to_check_raw_sketch_output=False, need_generation=True):
    def helper(bound=0):
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(TIME_LIMIT_FOR_CONSTRAINTS)
        codes = ''
        examples_list = []
        for prop in hard_properties:
            tmp = perturbation.get_hard_constraints_code_helper(prop, function_name, example_types, examples, bound=bound, to_check_raw_sketch_output=to_check_raw_sketch_output, need_generation=need_generation)
            codes += tmp[0]
            examples_list.append(tmp[1])
        # signal.alarm(0)
        return codes, examples_list

    print('------ Begin get_hard_constraints_code for %s ------'  % hard_properties)
    t1_start = get_time()
    codes = helper(EXAMPLE_BOUND)
    # codes = ''
    # try:
    #     codes = helper()
    # except Exception as err:
    #     print('Generating hard constraints of %s has error: %s\nTry to generate with bounds %s' % (hard_properties,err,EXAMPLE_BOUND))
    #     codes = helper(EXAMPLE_BOUND)
    t1_stop = get_time()
    print('Used time: %s' % ((t1_stop-t1_start)))
    print('------ End get_hard_constraints_code ------')
    return codes

def get_examples_types(code, spec_name):
    print('Extrating example types')
    type_pattern = '(\w+\s*(\[[\w*+\s]+\]\s*)*)'
    match = re.search(r'%s\s+%s\s*\((.*)\)' % (type_pattern, spec_name), code)
    if match and len(match.groups()) == 3:
        return_type_str = match.group(1).strip()
        arg_list_str = match.group(3).strip()
    else:
        raise ValueError('Cannot get function signature of %s from\n %s' % (spec_name, code))

    return_type = get_type(return_type_str, code)
    arg_type_list = []
    for arg in arg_list_str.split(','):
        if arg.startswith('ref'):
            raise ValueError('Do not support ref type: %s' % arg)
        match = re.search(r'%s\s+' % type_pattern, arg)
        if match and len(match.groups()) > 0:
            arg_type_list.append(get_type(match.group(1), code))
        else:
            raise ValueError('Cannot find the type from arg: %s' % arg)

    return return_type, arg_type_list

def get_type(type_str, code):
    # TODO: Check the matrix type
    var_dic = {}
    type_size = -1
    # check whether the types contains any variable, e.g. int[N]
    match = re.search(r'\[(\d+)\]', type_str)
    if match and len(match.groups()) > 0:
        # the type int[10]
        # do nothing
        type_size = match.group(1)
    else:
        match = re.search(r'\[([\d*+]+)\]', type_str)
        if match and len(match.groups()) > 0:
            # the type int[2*3]
            size_str = match.group(1)
            type_size = str(eval(size_str))
            type_str = type_str.replace(size_str, type_size)
        else:
            match = re.search(r'\[([a-zA-Z]+)\]', type_str)
            if match and len(match.groups()) > 0:
                # the type int[N]
                v_name = match.group(1)
                if v_name not in var_dic:
                    match = re.search(r'int\s+%s\s*=\s*(\d+)\s*;' % v_name, code)
                    if match and len(match.groups()) == 1:
                        var_dic[v_name] = match.group(1)
                type_size = var_dic[v_name]
                type_str = type_str.replace(v_name, type_size)
            else:
                match = re.search(r'\[([a-zA-Z\d*+]+)\]', type_str)
                if match and len(match.groups()) > 0:
                    # it contains a variable * a variable, so we need to find the value
                    v_names = []
                    v_str = match.group(1)
                    v_val = v_str
                    for t in v_str.split('*'):
                        for tt in t.split('+'):
                            if (not tt.isdigit()) and (tt not in v_names):
                                v_names.append(tt)
                    for v_name in v_names:
                        if v_name not in var_dic:
                            match = re.search(r'int\s+%s\s*=\s*(\d+)\s*;' % v_name, code)
                            if match and len(match.groups()) == 1:
                                var_dic[v_name] = match.group(1)
                                v_val = v_val.replace(v_name, var_dic[v_name])
                            else:
                                raise ValueError('Cannot find the value for %s' % v_name)
                    type_size = str(eval(v_val))
                    type_str = type_str.replace(v_str, type_size)
                else:
                    # not an array
                    pass
    type_str = type_str.strip()
    python_type = ''
    if type_size != -1:
        # primitive type: int, bit, etc.
        if type_str.startswith('bit'):
            python_type = 'bit_list_%s' % type_size
        elif type_str.startswith('int'):
            python_type = 'int_list_%s' % type_size
        else:
            raise ValueError('TODO: Check other types: %s' % type_str)
    else:
        python_type = type_str

    return type_str, python_type

def generate_input(num, arg_type_list):
    print('Generating inputs')
    def generate_one_helper(p_type):
        if p_type == 'bit':
            return random.randint(0,1)
        elif p_type == 'int':
            # TODO: check this!!
            # Sketch can only complete int holes with non-negative int
            # return random.randint(-10,10)
            return random.randint(0,10)
        elif p_type == 'char':
            # return random.choice(string.ascii_lowercase)
            return random.choice(['a','b'])
        else:
            print('TODO: Check other types:', p_type)

    inputs = []
    v_dict = {}
    # for function like fun(bit x), we can only have at most two input examples
    # We try 10 more times
    num_bound = num + 10
    while len(inputs) < num and num_bound > 0:
        num_bound -= 1
        e_in = []
        for _, p_type in arg_type_list:
            t = p_type.split('_')
            if len(t) == 1:
                # primitive type
                e_in.append(generate_one_helper(p_type))
            elif len(t) == 2:
                # int_N for other input array of size int_N
                t, vname = t
                v_dict[vname] = (generate_one_helper(t) + 1) % 7
                e_in.append(v_dict[vname])
            else:
                # list
                t, _, size = t
                if not size.isdigit():
                    size = v_dict[size]
                e_in.append([generate_one_helper(t) for _ in range(int(size))])
        if e_in not in inputs:
            inputs.append(e_in)
    return inputs

def init_test(benchmark_dir, output_dir, pbe_sketch_file=None, original_code_file=None, example_types=None, examples=None, properties=None, hard_properties=None, number_of_examples=3):
    sk_file_dir = os.path.dirname(output_dir)
    sk_file = os.path.join(sk_file_dir, benchmark_dir+'.sk')
    if not original_code_file:
        original_code_file = os.path.join(sk_file_dir, benchmark_dir+'_output.sk')
    if not os.path.isfile(original_code_file):
        # synthesize the original code
        print('Synthsizing orignial code')
        c = subprocess.run(["sketch", "--fe-timeout", "5", sk_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sketch_out = c.stdout.decode('utf-8')
        total_time = 0
        synthesized_code = ''
        match = re.search(r'Total time = (\d+)', sketch_out)
        if match and len(match.groups()) > 0:
            total_time = match.group(1)
            print('Total time:', total_time)
        else:
            raise ValueError('Cannot get the total time from \n%s' % sketch_out)
        original_code = 'original_code'
        match = re.search(r'(void.*implements.*)', sketch_out)
        if match and len(match.groups()) > 0:
            function_line = match.group(1)
            try:
                start_index = sketch_out.index(function_line)
            except ValueError:
                print('Error: Cannot find function line %s from\n%s\n' % (function_line, sketch_out))
                raise
            try:
                end_index = sketch_out.index('\n}\n', start_index+1) + 3
                original_code = sketch_out[start_index:end_index]
            except ValueError:
                try:
                    # The synthesized function is empty
                    end_index = sketch_out.index('\n{ }\n', start_index+1) + 5
                    original_code = sketch_out[start_index:end_index]
                except ValueError:
                    print('Error: Cannot find the end of the function from\n%s\n' % (sketch_out,))
                    raise
            match = re.search(r'void\s+(\w+).+implements\s+(\w+)', function_line)
            if match and len(match.groups()) == 2:
                function_name = match.group(1)
                spec_name = match.group(2)
            else:
                raise ValueError('Error: Cannot find function name and specification name from %s\n' % (function_line, ))
            if 'implements' in original_code:
                s1 = original_code.index('implements')
                s2 = original_code.index('\n', s1+1)
                pbe_function_name = 'pbe_' + function_name
                original_code = '%simplements %s%s' % (original_code[:s1], pbe_function_name, original_code[s2:])
                f_start = sketch_out.index('/* BEGIN PACKAGE ANONYMOUS*/')
                f_end = sketch_out.index('[SKETCH] DONE')
                original_code = sketch_out[f_start:start_index] + original_code + sketch_out[end_index:f_end]
        else:
            raise ValueError('Cannot get the correct output from\n%s' % sketch_out)
        with open(original_code_file, 'w') as out_file:
            out_file.write(original_code)
    else:
        with open(original_code_file) as in_file:
            original_code = in_file.read()
        match = re.search(r'void\s+(\w+).+implements\s+\w+', original_code)
        if match and len(match.groups()) == 1:
            function_name = match.group(1)
            pbe_function_name = 'pbe_' + function_name
        else:
            raise ValueError('Error: Cannot find function name from\n%s\n' % (original_code, ))

    sk_code = None
    with open(sk_file) as in_file:
        sk_code = in_file.read()
    match = re.search(r'\s+%s.+implements\s+(\w+)' % function_name, sk_code)
    if match and len(match.groups()) == 1:
        spec_name = match.group(1)
    elif function_name[0] == '_':
        # Sometimes Sketch will prefix the function's name with _
        function_name = function_name[1:]
        match = re.search(r'\s+%s.+implements\s+(\w+)' % function_name, sk_code)
        if match and len(match.groups()) == 1:
            spec_name = match.group(1)
        else:
            raise ValueError('Cannot extract the spec of %s from\n%s' % (function_name, sk_code))
    else:
        raise ValueError('Cannot extract the spec of %s from\n%s' % (function_name, sk_code))

    if not pbe_sketch_file:
        pbe_sketch_file = os.path.join(sk_file_dir, benchmark_dir+'_pbe.sk')
    if args.direct_prop:
        pbe_sketch_file = os.path.join(sk_file_dir, benchmark_dir+'_prop.sk')
        assert os.path.isfile(pbe_sketch_file)
    if not os.path.isfile(pbe_sketch_file):
        # extract the pbe_sketch_code
        print('Extracting pbe code')
        sk_file_content = ''
        with open(sk_file) as f:
            sk_file_content = f.read()
        sk_file_content += '\n' # To ensure there is '\n' after the end '}' of a function
        pbe_code = 'pbe_code'
        # To copy other helper functions such as generators
        # pbe_code = re.sub('\s*implements\s+%s' % spec_name, ' ', sk_file_content)
        # pbe_code = pbe_code.replace(function_name, pbe_function_name)

        match = re.search(r'(.+%s.+implements\s+%s)' % (function_name, spec_name), sk_file_content)
        if match and len(match.groups()) > 0:
            function_line = match.group(1)
            try:
                start_index = sk_file_content.index(function_line)
            except ValueError:
                print('Error: Cannot find function line %s from\n%s\n' % (function_line, sk_file_content))
                raise
            try:
                end_index = sk_file_content.index('\n}\n', start_index+1)
                pbe_code = sk_file_content[:start_index] + re.sub('\s*implements\s+%s' % spec_name, ' ', sk_file_content[start_index:end_index+3]).replace(function_name, pbe_function_name) + sk_file_content[end_index+3:]
            except ValueError:
                try:
                    # The synthesized function is empty
                    end_index = sk_file_content.index('\n{ }\n', start_index+1)
                    pbe_code = sk_file_content[:start_index] + re.sub('\s*implements\s+%s' % spec_name, ' ', sk_file_content[start_index:end_index+5]).replace(function_name, pbe_function_name) + sk_file_content[end_index+5:]
                except ValueError:
                    print('Error: Cannot find the end of the function from\n%s\n' % (sk_file_content,))
                    raise
            #if 'implements' in pbe_code:
            #    pbe_code_1, pbe_code_2 = pbe_code.split('implements', maxsplit=1)
            #    match = re.search(r'(\s{\s)', pbe_code_2)
            #    if match and len(match.groups()) > 0:
            #        body_begin = match.group(1)
            #    else:
            #        print('Error match body begin')
            #        exit(-1)
            #    s2 = pbe_code_2.index(body_begin)
            #    pbe_code = pbe_code_1 + pbe_code_2[s2:]
            #    pbe_code = pbe_code.replace(function_name, pbe_function_name)
        else:
            # print('Deleting this benchmark')
            # rmtree(sk_file_dir)
            raise ValueError('Cannot extract the pbe code from\n%s' % sk_file_content)

        with open(pbe_sketch_file, 'w') as out_file:
            out_file.write(pbe_code)

    # Check whether we need to load the examples from a file
    if LOAD_EXAMPLE_FROM_FILE:
        if USE_OWN_GENERATOR:
            example_types, examples = load_example(os.path.join(sk_file_dir, OWN_GENERATED_EXAMPLES_FILE), REPEAT_INDEX, number_of_examples)
        else:
            example_types, examples = load_example_wrapper(os.path.join(sk_file_dir, FIXED_EXAMPLES_FILE), REPEAT_INDEX, number_of_examples)
            print('Loaded %dth example set' % REPEAT_INDEX)
            print(example_types)
            print(examples)

    # Use self defined generator to generate examples
    if USE_OWN_GENERATOR:
        get_examples_module = importlib.import_module('%s.%s.get_examples' % ('.'.join(ARGS_DIR), benchmark_dir))
        get_examples = getattr(get_examples_module, 'get_examples')
        example_types = getattr(get_examples_module, 'example_types')
        examples = get_examples(number_of_examples)

    if example_types is None:
        try:
            return_type, arg_type_list = get_examples_types(sk_code, spec_name)
        except KeyError:
            raise ValueError('Illegal Type')
        example_types = [[x[1] for x in arg_type_list], [return_type[1]],]
    else:
        arg_type_list = [('', x) for x in example_types[0]]
        return_type = ['', example_types[1][0]]
    # manually generate the examples
    if examples is None:
        example_inputs = generate_input(number_of_examples, arg_type_list)
        examples = [ ]
        for e_in in example_inputs:
            examples.append((e_in, synthesize_output(benchmark_dir, return_type, arg_type_list, e_in, spec_name, sk_code)))
    if len(example_types[0]) == 0:
        # remove benchmarks has no inputs
        raise ValueError('this function %s has no input' % benchmark_dir)
    if len(example_types[0]) == 1 and example_types[0][0] == 'bit':
        raise ValueError('this function %s has only a bit input' % benchmark_dir)
    if example_types[1][0] == 'void':
        raise ValueError('this function %s has no output' % benchmark_dir)
    constraints_failed =  get_original_constraints_code(pbe_function_name, example_types, examples)
    constraints_soft_fixed = None
    if properties:
        if ONLY_USE_POSITIVE_PROPERTIES:
            properties = [x for x in properties if not x.startswith('not')]
        print('------ Begin get_soft_constraints_code for %s ------' % properties)
        t1_start = get_time()
        tmp_cons = get_soft_constraints_code(properties, pbe_function_name, example_types, examples)[0]
        t1_stop = get_time()
        print('Used time: %s' % ((t1_stop-t1_start)))
        constraints_soft_fixed = constraints_failed + tmp_cons
        print('------ End get_soft_constraints_code ------')

    if LOAD_PROPERTIES:
        # we have loaded properties from properties.conf
        hard_properties = BENCHMARK_PROPERTY_DICT.get(benchmark_dir+'.sk', None)
        if hard_properties is None:
            raise ValueError('Missing properties for %s' % benchmark_dir)
        print('Loaded %s: %s' % (benchmark_dir, ','.join(hard_properties)))
        if len(hard_properties) == 0 or hard_properties[0] == 'none':
            hard_properties = None

    if hard_properties:
        if ONLY_USE_POSITIVE_PROPERTIES:
            hard_properties = [x for x in hard_properties if not x.startswith('not')]

    if ONLY_COUNTING_NUM_OF_EXAMPLES:
        if hard_properties:
            # BEN_NUM_OF_EXAMPLES_DICT[benchmark_dir] = BEN_NUM_OF_EXAMPLES_DICT.get(benchmark_dir, 0) + sum(map(len, get_hard_constraints_code(hard_properties, pbe_function_name, example_types, examples)[1]))
            BEN_NUM_OF_POS_EXAMPLES_DICT[benchmark_dir] = BEN_NUM_OF_POS_EXAMPLES_DICT.get(benchmark_dir, 0) + sum(map(len, get_hard_constraints_code([p for p in hard_properties if not p.startswith('not_')], pbe_function_name, example_types, examples)[1]))
            BEN_NUM_OF_NEG_EXAMPLES_DICT[benchmark_dir] = BEN_NUM_OF_NEG_EXAMPLES_DICT.get(benchmark_dir, 0) + sum(map(len, get_hard_constraints_code([p for p in hard_properties if p.startswith('not_')], pbe_function_name, example_types, examples)[1]))
        else:
            pass
            # BEN_NUM_OF_EXAMPLES_DICT[benchmark_dir] = BEN_NUM_OF_EXAMPLES_DICT.get(benchmark_dir, 0)
        constraints_hard_fixed = ''
    else:
        constraints_hard_fixed = hard_properties and (constraints_failed + get_hard_constraints_code(hard_properties, pbe_function_name, example_types, examples)[0])
    return original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples, spec_name

def synthesize_output(benchmark_dir, return_type, arg_type_list, e_in, spec_name, sk_code):
    print('Synthesizing output')
    template = '''
harness void synthesize_output() {
  assert ?? == %s(%s);
}
''' % (spec_name, perturbation.str_inputs([x[1] for x in arg_type_list], e_in))
    sk_code = sk_code + template
    tmp_file = '/tmp/%s_%s.sk' % (benchmark_dir, datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'))
    with open(tmp_file, 'w') as out_file:
        out_file.write(sk_code)
    c = subprocess.run(["sketch", "--fe-timeout", "5", tmp_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sketch_out = c.stdout.decode('utf-8')
    total_time = 0
    match = re.search(r'Total time = (\d+)', sketch_out)
    if match and len(match.groups()) > 0:
        total_time = match.group(1)
        print('Total time:', total_time)
    else:
        raise ValueError('Cannot get the total time from \n%s' % sketch_out)
    if return_type[1] == 'bit' or return_type[1] == 'int':
        match = re.search(r'assert \((\d+) == \w+\);', sketch_out)
        if match and len(match.groups()) > 0:
            return [int(match.group(1))]
        else:
            raise ValueError('Cannot extract the output from\n%s ' % sketch_out)
    elif 'list' in return_type[1]:
        if 'char' in return_type[1]:
            match = re.search(r'assert \(+(\{[a-z\',]+\})\)* == \w+\);', sketch_out)
        else:
            match = re.search(r'assert \(+(\{[\d,]+\})\)* == \w+\);', sketch_out)
        if match and len(match.groups()) > 0:
            r = match.group(1)[1:-1].split(',')
            if 'bit' in return_type[1] or 'int' in return_type[1]:
                r = [int(i) for i in r]
            if 'char' in return_type[1]:
                r = [i[1] for i in r]
            print([r])
            return [r]
        else:
            raise ValueError('Cannot extract the output from\n%s ' % sketch_out)


def interact_with_a_user(properties, benchmark_dir, pbe_sketch_file, output_dir, example_types, prop_examples_dict, spec_name=None):
    def choose_prop_by_spec(prop, examples, output_dir):
        function_signatures = [ 'void ' + spec_name, ]
        tmp_constraints = get_hard_constraints_code([prop, ], spec_name, example_types, examples, need_generation=False)[0]
        try:
            run_test(benchmark_dir, pbe_sketch_file, function_signatures, None, output_dir, constraints=tmp_constraints, need_cmp=False)
        except ValueError as err:
            print("Reject the prop {0} with error: {1}".format(prop, err))
            return False
        else:
            return True

    def print_example(examples, negative=False):
        for example in examples:
            tmp = '    %s => %s'
            if negative:
                tmp = '    %s !=> %s'
            print( tmp % (
                perturbation.str_inputs(example_types[0], example[0]),
                perturbation.str_outputs(example_types[1], example[1]),
                )
            )

    def show_examples(prop, examples):
        print('Please check the following constraints:')
        num_of_positive_examples_to_show = min(NUM_OF_POSITIVE_EXAMPLES_TO_SHOW, len(examples))
        num_of_negative_examples_to_show = min(NUM_OF_NEGATIVE_EXAMPLES_TO_SHOW, len(examples))
        return_examples = []
        if prop.startswith('not_'):
            # negative properties
            print('If NONE of them are satisfied, input 0. Otherwise, input 1.')
            return_examples = random.sample(examples, num_of_negative_examples_to_show)
            print_example(return_examples, negative=True)
        else:
            # positive properties
            print('If ALL of them are satisfied, input 1. Otherwise, input 0.')
            return_examples = random.sample(examples, num_of_positive_examples_to_show)
            print_example(return_examples)
        return return_examples

    if USE_SPEC_AS_USER:
        tmp_output_dir = os.path.join(output_dir, 'interaction')
        os.makedirs(tmp_output_dir, exist_ok=True)

    return_props = []

    if INFER_NEG_PROP_BY_POS_PROP:
        # Add the negative property if the corresponding positive property is not applicable because of imcompatible perturbed examples
        for prop in properties:
            if prop.startswith('not_'):
                if prop[4:] not in properties:
                    print('Add %s because the corresponding positive property is not in the applicable properties' % (prop, ))
                    return_props.append(prop)

    for prop in properties:
        if INFER_NEG_PROP_BY_POS_PROP and prop.startswith('not_'):
            continue
        examples = show_examples(prop, prop_examples_dict[prop])
        if USE_SPEC_AS_USER:
            # use spec to auto choose property
            if choose_prop_by_spec(prop, examples, tmp_output_dir):
                return_props.append(prop)
            elif INFER_NEG_PROP_BY_POS_PROP:
                return_props.append('not_'+prop)
        else:
            input_invalid = True
            while input_invalid:
                try:
                    res = int(input('0 for wrong and 1 for right: '))
                except ValueError:
                    print('please input 0 or 1!!')
                else:
                    if res == 0 or res == 1:
                        input_invalid = False
                    else:
                        print('please input 0 or 1!!')
            if res == 1:
                return_props.append(prop)

    return return_props


def incremental_test(benchmark_dir, pbe_sketch_file, original_code_file, output_dir, pbe_function_name, example_types, examples, raw_sketch_output=None, spec_name=None):
    def check_raw_sketch_output_with_property(constraints):
        # write the raw_sketch_output to file first
        raw_sketch_output_file = os.path.join(tmp_output_dir, 'check_raw_sketch_%s.sk' % datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'))
        with open(raw_sketch_output_file, 'w') as out_file:
            out_file.write(raw_sketch_output)
            out_file.write(constraints)
        try:
            run_test(benchmark_dir, raw_sketch_output_file, function_signatures, None, None, need_cmp=False)
        except ValueError as err:
            print("Check raw sketch error: {0}".format(err))
            return False
        else:
            return True

    def update_conflicts(prop_dict, prop1, prop2):
        if prop1 in prop_dict:
            prop_dict[prop1].append(prop2)
        else:
            prop_dict[prop1] = [prop2,]
        if prop2 in prop_dict:
            prop_dict[prop2].append(prop1)
        else:
            prop_dict[prop2] = [prop1,]

    def conflict_helper(prop_dict, p1, p2):
        # print('conflict_helper:', prop_dict, p1, p2)
        if p2 in prop_dict and p1 in prop_dict[p2]:
            return True
        return False

    def conflict(prop_dict, prop_set, prop):
        for p1 in prop_set:
            if conflict_helper(prop_dict, p1, prop):
                return True
        return False

    if raw_sketch_output:
        to_check_raw_sketch_output = USE_DEFAULT_RAW_SKETCH
    else:
        to_check_raw_sketch_output = False

    function_signatures = [ 'void '+ pbe_function_name ]
    test_times = 1
    candidate_properties = []
    applicable_properties = []
    prop_soft_constr_dict = {}
    prop_examples_dict = {}
    trying_prop_result_dict = {}
    hard_constraints =  get_original_constraints_code(pbe_function_name, example_types, examples)
    tmp_output_dir = os.path.join(output_dir, '1')
    if not os.path.isdir(tmp_output_dir):
        os.makedirs(tmp_output_dir, exist_ok=True)
    print('------ Begin generating constraints for %s ------' % PERTURBATION_PROPERTIES)
    t1_start = get_time()
    for prop in PERTURBATION_PROPERTIES:
        try:
            # tmp = get_soft_constraints_code([prop,], pbe_function_name, example_types, examples)
            tmp = get_hard_constraints_code([prop,], pbe_function_name, example_types, examples)
            if tmp[0]:
                prop_soft_constr_dict[prop] = tmp[0]
                prop_examples_dict[prop] = tmp[1][0]
                applicable_properties.append(prop)
        except Exception as err:
            # print('Generating soft constraints of %s has error: %s' % (prop,err))
            print('Generating constraints of %s has error: %s' % (prop,err))
    t1_stop = get_time()
    print('Used time: %s' % ((t1_stop-t1_start)))
    # print('------ End get_soft_constraints_code ------')
    print('------ End generating constraints ------')

    if INTERACTIVE_LEVEL > 0:
        # ask a user to pick the correct perturbed examples
        props = interact_with_a_user(applicable_properties, benchmark_dir, pbe_sketch_file, output_dir, example_types, prop_examples_dict, spec_name)
        if INTERACTIVE_LEVEL == 1:
            applicable_properties = props
        elif INTERACTIVE_LEVEL == 2:
            if to_check_raw_sketch_output:
                print('First check if the program synthesized by raw Sketch satisfies the property set:', props)
                tmp_constraints = ''
                for prop in props:
                    tmp_constraints += get_hard_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], to_check_raw_sketch_output=to_check_raw_sketch_output, need_generation=False)[0]

                if check_raw_sketch_output_with_property(tmp_constraints):
                    print('Choose program synthesized by raw Sketch, as it satisfies:', props)
                    return

            print('Using properties:', props)
            soft_constraints = ''
            for prop in props:
                if prop.startswith('not_') and INFERENCE_STRATEGY != ENFORCEMENT_STRATEGY:
                    # Using different enforcement strategy from inference strategy for the negative properies and synthesize it again.
                    t_y_percent =  ENFORCEMENT_STRATEGY.split('at_least_')
                    if len(t_y_percent) > 1:
                        soft_constraints += get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], y_percent=float(t_y_percent[1]), need_generation=False)[0]
                    else:
                        soft_constraints += get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], need_generation=False)[0]
                else:
                    soft_constraints += prop_soft_constr_dict[prop]
            try:
                run_test(benchmark_dir, pbe_sketch_file,
                         function_signatures, original_code_file, tmp_output_dir, test_times,
                         hard_constraints + soft_constraints)
            except ValueError as err:
                # If the property set only contains one positive property, we try use the negative one then.
                if INVERT_ONE_POSITIVE_PROP and len(props) == 1 and not props[0].startswith('not_'):
                    print('Failed by %s, now try to use the negative one' % props[0])
                    prop = 'not_' + props[0]
                    soft_constraints = ''
                    if prop.startswith('not_') and INFERENCE_STRATEGY != ENFORCEMENT_STRATEGY:
                        # Using different enforcement strategy from inference strategy for the negative properies and synthesize it again.
                        t_y_percent =  ENFORCEMENT_STRATEGY.split('at_least_')
                        if len(t_y_percent) > 1:
                            soft_constraints += get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], y_percent=float(t_y_percent[1]), need_generation=False)[0]
                        else:
                            soft_constraints += get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], need_generation=False)[0]
                    else:
                        soft_constraints += prop_soft_constr_dict[prop]
                    try:
                        run_test(benchmark_dir, pbe_sketch_file,
                                 function_signatures, original_code_file, tmp_output_dir, test_times,
                                 hard_constraints + soft_constraints)
                    except ValueError as err:
                        print("After inferring, run test error: {0}".format(err))
                        raise
                else:
                    print("After inferring, run test error: {0}".format(err))
                    raise
            return

    for prop in applicable_properties:
        soft_constraints = prop_soft_constr_dict[prop]
        print('Trying properties:', prop)
        try:
            tmp_res = run_test(benchmark_dir, pbe_sketch_file,
                    function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)[0]
        except ValueError as err:
            #print("Run test error: {0}".format(err))
            pass
        else:
            candidate_properties.append(prop)
            trying_prop_result_dict[prop] = tmp_res

    tmp_output_dir = os.path.join(output_dir, 'result')
    if not os.path.isdir(tmp_output_dir):
        os.makedirs(tmp_output_dir, exist_ok=True)
    if len(candidate_properties) == 0:
        print('No applicable property, so only use user-provided examples')
        # try:
        #     run_test(benchmark_dir, pbe_sketch_file,
        #             function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints)
        # except ValueError as err:
        #     #print("Run test error: {0}".format(err))
        #     raise
    elif len(candidate_properties) == 1:
        prop = candidate_properties[0]
        if to_check_raw_sketch_output:
            print('First check if the program synthesized by raw Sketch satisfies the property:', prop)
            tmp_constraints = get_hard_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], to_check_raw_sketch_output=to_check_raw_sketch_output, need_generation=False)[0]
            if check_raw_sketch_output_with_property(tmp_constraints):
                print('Choose program synthesized by raw Sketch, as it satisfies:', prop)
                return

        print('Using property:', prop)
        if prop.startswith('not_') and INFERENCE_STRATEGY != ENFORCEMENT_STRATEGY:
            # Using different enforcement strategy from inference strategy for the negative properies and synthesize it again.
            t_y_percent =  ENFORCEMENT_STRATEGY.split('at_least_')
            if len(t_y_percent) > 1:
                soft_constraints = get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], y_percent=float(t_y_percent[1]), need_generation=False)[0]
            else:
                soft_constraints = get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], need_generation=False)[0]
            try:
                run_test(benchmark_dir, pbe_sketch_file,
                        function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)
            except ValueError as err:
                print("After inferring, run test error: {0}".format(err))
                raise
        else:
            # just return the cached result
            print(trying_prop_result_dict[prop])
        # Return the cached result instead of rerunning it, as we let Sketch behave deterministically
        # soft_constraints = prop_soft_constr_dict[prop]
        # try:
        #     run_test(benchmark_dir, pbe_sketch_file,
        #             function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)
        # except ValueError as err:
        #     #print("Run test error: {0}".format(err))
        #     raise
    else:
        current_property_sets = [[p,] for p in candidate_properties]
        conflict_property_dict = {}
        for p in PERTURBATION_PROPERTIES:
            if not p.startswith('not_'):
                update_conflicts(conflict_property_dict, p, 'not_'+p)
        new_current_property_set = None
        while len(current_property_sets) > 1:
            new_current_property_set = []
            tested_property_set_strs = []
            for prop_set in current_property_sets:
                for prop in candidate_properties:
                    if prop in prop_set: continue
                    if conflict(conflict_property_dict, prop_set, prop): continue
                    tmp_prop_set = prop_set + [prop,]
                    tmp_prop_set.sort()
                    tmp_prop_set_str = ''.join(tmp_prop_set)
                    if tmp_prop_set_str in tested_property_set_strs: continue
                    tested_property_set_strs.append(tmp_prop_set_str)
                    tmp_output_dir = os.path.join(output_dir, str(len(tmp_prop_set)))
                    if not os.path.isdir(tmp_output_dir):
                        os.makedirs(tmp_output_dir, exist_ok=True)
                    soft_constraints = ''.join([prop_soft_constr_dict[p] for p in tmp_prop_set])
                    print('Trying properties:', tmp_prop_set)
                    try:
                        tmp_res = run_test(benchmark_dir, pbe_sketch_file,
                                function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)[0]
                    except ValueError as err:
                        # print("Run test error: {0}".format(err))
                        # print('updating conflict', tmp_prop_set)
                        if len(tmp_prop_set) == 2: update_conflicts(conflict_property_dict, tmp_prop_set[0], tmp_prop_set[1])
                    else:
                        new_current_property_set.append(tmp_prop_set)
                        trying_prop_result_dict[tmp_prop_set_str] = tmp_res
            if len(new_current_property_set) == 0:
                # use the current property set in the last iteration
                break
            current_property_sets = new_current_property_set[:]

        tmp_output_dir = os.path.join(output_dir, 'result')
        if not os.path.isdir(tmp_output_dir):
            os.makedirs(tmp_output_dir, exist_ok=True)
        if len(current_property_sets) == 0:
            print('No applicable property, so only use user-provided examples')
            # try:
            #     run_test(benchmark_dir, pbe_sketch_file,
            #             function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints)
            # except ValueError as err:
            #     #print("Run test error: {0}".format(err))
            #     raise
        elif len(current_property_sets) >= 1:
            if USE_RANKING_STRATEGY:
                # Now use the ranking function to return one property set.
                current_property_sets = [perturbation.rank_property_sets(current_property_sets),]
            # Test all the prop sets
            for props in reversed(current_property_sets):
                if to_check_raw_sketch_output:
                    print('First check if the program synthesized by raw Sketch satisfies the property set:', props)
                    tmp_constraints = ''
                    for prop in props:
                        tmp_constraints += get_hard_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], to_check_raw_sketch_output=to_check_raw_sketch_output, need_generation=False)[0]
                    if check_raw_sketch_output_with_property(tmp_constraints):
                        print('Choose program synthesized by raw Sketch, as it satisfies:', props)
                        continue

                print('Using properties:', props)
                tmp_prop_set = props[:]
                tmp_prop_set.sort()
                tmp_prop_set_str = ''.join(tmp_prop_set)
                prop_contain_neg = False
                soft_constraints = ''
                for prop in props:
                    if prop.startswith('not_') and INFERENCE_STRATEGY != ENFORCEMENT_STRATEGY:
                        # Using different enforcement strategy from inference strategy for the negative properies and synthesize it again.
                        prop_contain_neg = True
                        t_y_percent =  ENFORCEMENT_STRATEGY.split('at_least_')
                        if len(t_y_percent) > 1:
                            soft_constraints += get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], y_percent=float(t_y_percent[1]), need_generation=False)[0]
                        else:
                            soft_constraints += get_soft_constraints_code([prop, ], pbe_function_name, example_types, prop_examples_dict[prop], need_generation=False)[0]
                    else:
                        soft_constraints += prop_soft_constr_dict[prop]
                if prop_contain_neg:
                    try:
                        run_test(benchmark_dir, pbe_sketch_file,
                                 function_signatures, original_code_file, tmp_output_dir, test_times,
                                 hard_constraints + soft_constraints)
                    except ValueError as err:
                        print("After inferring, run test error: {0}".format(err))
                        # raise
                        # in order to test all the property sets
                        pass
                else:
                    print(trying_prop_result_dict[tmp_prop_set_str])
                # Return the cached result instead of rerunning it, as we let Sketch behave deterministically
                # soft_constraints = ''.join([prop_soft_constr_dict[p] for p in props])
                # try:
                #     run_test(benchmark_dir, pbe_sketch_file,
                #             function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)
                # except ValueError as err:
                #     #print("Run test error: {0}".format(err))
                #     raise
        else:
            print('Error! This error should not happen!')

def run_test(benchmark_dir, pbe_sketch_file, function_signatures, original_code_file, output_dir, test_times=1, constraints=None, need_cmp=True):
    cnt_right = 0

    if constraints is not None and constraints:
        # build the sketch file first
        pbe_sketch_file = copyfile(
                pbe_sketch_file,
                os.path.join(
                    output_dir,
                    '%s_pbe_%s.sk' % (benchmark_dir,
                        datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'))))
        with open(pbe_sketch_file, 'a') as out_file:
            out_file.write(constraints)

    for _ in range(test_times):
        t1_start = get_time()
        if args.direct_prop:
            # increase the timeout bound
            c = subprocess.run(["sketch", "--slv-seed", "7", "--fe-timeout", "30", "--bnd-mbits", "11", pbe_sketch_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            c = subprocess.run(["sketch", "--slv-seed", "7", "--fe-timeout", "5", "--bnd-mbits", "11", pbe_sketch_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t1_stop = get_time()
        print('Used time: %s' % ((t1_stop-t1_start)))
        sketch_out = c.stdout.decode('utf-8')
        total_time = 0
        synthesized_code = ''
        match = re.search(r'Total time = (\d+)', sketch_out)
        if match and len(match.groups()) > 0:
            total_time = match.group(1)
            print('Total time:', total_time)
        else:
            raise ValueError('Cannot get the total time from \n%s' % sketch_out)
        for f in function_signatures:
            try:
                start_index = sketch_out.index(f)
            except ValueError:
                print('Can not find function %s from\n%s' % (f, sketch_out))
                raise
            try:
                end_index = sketch_out.index('\n}\n', start_index+1) + 3
                tmp_code = sketch_out[start_index:end_index]
            except ValueError:
                try:
                    # The synthesized function is empty
                    end_index = sketch_out.index('\n{ }\n', start_index+1) + 5
                    tmp_code = sketch_out[start_index:end_index]
                except ValueError:
                    print('Can not find the end of the function %s from\n%s' % (f, sketch_out))
                    raise
            if 'implements' in tmp_code:
                print('Find implements in tmp_code!')
                s1 = tmp_code.index('implements')
                s2 = tmp_code.index('\n', s1+1)
                tmp_code = tmp_code[:s1] + tmp_code[s2:]
            synthesized_code += tmp_code
            f_start = sketch_out.index('/* BEGIN PACKAGE ANONYMOUS*/')
            f_end = sketch_out.index('[SKETCH] DONE')
            synthesized_code_to_return = sketch_out[f_start:start_index] + tmp_code + sketch_out[end_index:f_end]

        if not need_cmp: return None

        cmp_code_file = copyfile(
                original_code_file,
                os.path.join(
                    output_dir,
                    'cmp_%s_%s.sk' % (benchmark_dir,
                        datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'))))
        with open(cmp_code_file, 'a') as out_file:
            out_file.write(synthesized_code)

        c = subprocess.run(["sketch", "--fe-timeout", "2", cmp_code_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cmp_result = c.stdout.decode('utf-8')
        cmp_result_file = cmp_code_file + '.output'
        total_time = 0
        match = re.search(r'Total time = (\d+)', cmp_result)
        if match and len(match.groups()) > 0:
            total_time = match.group(1)
            print('Total time:', total_time)
        else:
            raise ValueError('Cannot get the total time from \n%s' % cmp_result)
        if 'UNSATISFIABLE' in cmp_result or 'Rejected' in cmp_result:
            cmp_result_file += '.wrong'
        # elif 'front-end timed out' in cmp_result:
        #     cmp_result_file += '.check'
        #     print('Sketch timeout! Please check this file manually %s' % cmp_code_file)
        else:
            cmp_result_file += '.right'
            cnt_right += 1

        with open(cmp_result_file, 'a') as out_file:
            out_file.write(cmp_result)
    #print('using constraints:\n', constraints)
    print('right rate: %d / %d || %s' % (cnt_right, test_times, cmp_result_file))
    return 'right rate: %d / %d || %s' % (cnt_right, test_times, cmp_result_file), synthesized_code_to_return

def test_all(test_type):
    for benchmark_dir in os.listdir(BENCHMARKS_DIR):
        test_one(benchmark_dir, test_type)

def test_one(benchmark_dir, test_type, number_of_examples=3):
    global BRUTE_PRESET_EXAMPLES
    path = os.path.join(BENCHMARKS_DIR, benchmark_dir)
    if not os.path.isdir(path): return

    print('====== Begin Test %s ======' % benchmark_dir)
    test_config_file = os.path.join(path, 'test_config.py')
    function_signatures = None
    test_times = 1
    output_dir = os.path.join(path, 'python_test')
    pbe_failed_output_dir = os.path.join(output_dir, 'failed')
    pbe_prop_output_dir = os.path.join(output_dir, 'prop')
    pbe_hard_fixed_output_dir = os.path.join(output_dir, 'hard_fixed')
    pbe_soft_fixed_output_dir = os.path.join(output_dir, 'soft_fixed')
    if not os.path.isdir(pbe_failed_output_dir):
        os.makedirs(pbe_failed_output_dir, exist_ok=True)
    if not os.path.isdir(pbe_prop_output_dir):
        os.makedirs(pbe_prop_output_dir, exist_ok=True)
    if not os.path.isdir(pbe_hard_fixed_output_dir):
        os.makedirs(pbe_hard_fixed_output_dir, exist_ok=True)
    if not os.path.isdir(pbe_soft_fixed_output_dir):
        os.makedirs(pbe_soft_fixed_output_dir, exist_ok=True)
    if os.path.isfile(test_config_file):
        test_config_model = '%s.%s.test_config' % ('.'.join(ARGS_DIR), benchmark_dir)
        test_config = importlib.import_module(test_config_model)
        test_times = getattr(test_config, 'times', 1)
        function_signatures = getattr(test_config, 'function_signatures', None)
        original_code_file = getattr(test_config, 'original_code_file', None)
        original_code_file = original_code_file and os.path.join(path, original_code_file)
        pbe_failed_sketch_file = getattr(test_config, 'pbe_failed_sketch_file', None)
        pbe_failed_sketch_file = pbe_failed_sketch_file and os.path.join(path, pbe_failed_sketch_file)
        pbe_sketch_file = pbe_failed_sketch_file
        pbe_fixed_sketch_file = getattr(test_config, 'pbe_fixed_sketch_file', None)
        pbe_fixed_sketch_file = pbe_fixed_sketch_file and os.path.join(path, pbe_fixed_sketch_file)
        # check whether we should generate original examples
        examples = getattr(test_config, 'examples', None)
        constraints_failed = ''
        constraints_hard_fixed = ''
        constraints_soft_fixed = ''
        properties = getattr(test_config, 'properties', None)
        hard_properties = getattr(test_config, 'hard_properties', None)
        if 'soft' not in test_type:
            properties = None
        if 'hard' not in test_type:
            hard_properties = None
        example_types = getattr(test_config, 'example_types', None)
        if USE_RANDOM_EXAMPLES or LOAD_EXAMPLE_FROM_FILE or JUST_GEN_RAND_EXAMPLE:
            examples = None
        if examples is None or not examples:
            # generate original examples
            if JUST_GEN_RAND_EXAMPLE:
                get_examples = getattr(test_config, 'get_examples', None)
                examples = get_examples and get_examples(number_of_examples)
            elif USE_RANDOM_EXAMPLES and not LOAD_EXAMPLE_FROM_FILE:
                if BRUTE_NEED_REMEMBER_EXAMPLES and BRUTE_PRESET_EXAMPLES is not None:
                    examples = BRUTE_PRESET_EXAMPLES
                else:
                    get_examples = getattr(test_config, 'get_examples', None)
                    examples = get_examples and get_examples(number_of_examples)
                    if BRUTE_NEED_REMEMBER_EXAMPLES and BRUTE_PRESET_EXAMPLES is None:
                        BRUTE_PRESET_EXAMPLES = examples
            # constraints_failed = test_config.get_original_constraints_code(examples)
            original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples, spec_name = init_test(benchmark_dir, output_dir, pbe_sketch_file, original_code_file, example_types, examples, properties, hard_properties, number_of_examples)
        else:
            pbe_function_name = getattr(test_config, 'function_name', None)
            if pbe_function_name is None:
                original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples, spec_name = init_test(benchmark_dir, output_dir, pbe_sketch_file, original_code_file, example_types, examples, properties, hard_properties, number_of_examples)
            else:
                constraints_failed = get_original_constraints_code(pbe_function_name, example_types, examples)
                constraints_soft_fixed = None
                if 'soft' in test_type and properties:
                    print('------ Begin get_soft_constraints_code for %s ------' % properties)
                    t1_start = get_time()
                    tmp_cons = get_soft_constraints_code(properties, pbe_function_name, example_types, examples)[0]
                    t1_stop = get_time()
                    print('Used time: %s' % ((t1_stop-t1_start)))
                    constraints_soft_fixed = constraints_failed + tmp_cons
                    print('------ End get_soft_constraints_code ------')
                if 'hard' in test_type:
                    constraints_hard_fixed = hard_properties and (constraints_failed + get_hard_constraints_code(hard_properties, pbe_function_name, example_types, examples)[0])
    else:
        try:
            original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples, spec_name = init_test(benchmark_dir, output_dir, number_of_examples=number_of_examples)
        except Exception as err:
            print("Init test error: {0}".format(err))
            # print('Deleting this benchmark')
            # comment out for incr test
            # rmtree(path)
            return

    if JUST_GEN_RAND_EXAMPLE:
        if USE_OWN_GENERATOR:
            save_examples(os.path.join(path, OWN_GENERATED_EXAMPLES_FILE), example_types, examples)
        else:
            save_examples(os.path.join(path, FIXED_EXAMPLES_FILE), example_types, examples)
        return


    if ONLY_COUNTING_NUM_OF_EXAMPLES:
        return

    if function_signatures is None:
        function_signatures = [ 'void '+ pbe_function_name ]
    if 'prop' in test_type:
        print('Test prop %s for %s times' % (pbe_sketch_file, test_times))
        try:
            raw_sketch_output = run_test(benchmark_dir, pbe_sketch_file,
                function_signatures, original_code_file, pbe_prop_output_dir, test_times, constraints_failed)[1]
        except ValueError as err:
            print("Run test error: {0}".format(err))
            # print('Deleting this benchmark')
            # rmtree(path)
            return
    if 'failed' in test_type:
        print('Test failed %s for %s times' % (pbe_sketch_file, test_times))
        try:
            raw_sketch_output = run_test(benchmark_dir, pbe_sketch_file,
                function_signatures, original_code_file, pbe_failed_output_dir, test_times, constraints_failed)[1]
        except ValueError as err:
            print("Run test error: {0}".format(err))
            # print('Deleting this benchmark')
            # rmtree(path)
            return
    if 'hard' in test_type:
        if constraints_hard_fixed:
            print('Test hard fixed %s for %s times' % (pbe_sketch_file, test_times))
            try:
                run_test(benchmark_dir, pbe_sketch_file,
                        function_signatures, original_code_file, pbe_hard_fixed_output_dir, test_times, constraints_hard_fixed)
            except ValueError as err:
                print("Run test error: {0}".format(err))
                # print('Deleting this benchmark')
                # rmtree(path)
                return
    if 'soft' in test_type:
        if constraints_soft_fixed:
            print('Test soft fixed %s for %s times' % (pbe_sketch_file, test_times))
            try:
                run_test(benchmark_dir, pbe_sketch_file,
                        function_signatures, original_code_file, pbe_soft_fixed_output_dir, test_times, constraints_soft_fixed)
            except ValueError as err:
                print("Run test error: {0}".format(err))
                # print('Deleting this benchmark')
                # rmtree(path)
                return
    if 'incr' in test_type:
        print('Test incrementally %s for %s times' % (pbe_sketch_file, test_times))
        inc_output_dir = os.path.join(output_dir, 'inc')
        if not os.path.isdir(inc_output_dir):
            os.makedirs(inc_output_dir)
        try:
            incremental_test(benchmark_dir, pbe_sketch_file, original_code_file, inc_output_dir, pbe_function_name, example_types, examples, raw_sketch_output=raw_sketch_output, spec_name=spec_name)
        except Exception as err:
            print('Incremental test error: {0}'.format(err))
            return
    print('====== End Test %s ======' % benchmark_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run tests for sketch benchmarks')
    parser.add_argument('-d', '--directory', help='sub benchmark directory')
    parser.add_argument('-t', '--test-type', help='type of test: failed, hard, soft, incr')
    parser.add_argument('-r', '--range', help='when benchmark\'s name contains +, a:b chooses benchmarks from list[a:b]')
    parser.add_argument('--repeat', type=int, default=1, help='times to repeat tests')
    parser.add_argument('--example-nums', help='numbers of examples')
    parser.add_argument('--random', help='use random examples', action='store_true')
    parser.add_argument('--bound-time', type=int, help='bound the seconds to generate the perturbed examples (bound the number of examples by default)')
    parser.add_argument('--bound-num', help='bound the number of examples by 128 by default. To bound ks, use 1000+bound')
    parser.add_argument('--percent', help='use x genearted examples', action='store_true')
    parser.add_argument('--just-gen', help='just genearte random examples', action='store_true')
    parser.add_argument('--load-example', help='use pre-generated random examples', action='store_true')
    # TODO: Really ugly solution to load some particular examples
    parser.add_argument('--example-id', help='set the id of pre-generated random example')
    parser.add_argument('--enforcement-strategy', help='how to enforce the negative property: disjunction / soft / at_least_30')
    parser.add_argument('--default-sketch', help='use the program synthesized by raw sketch if it satisfies the inferred propery set', action='store_true')
    parser.add_argument('--ranking', help='use ranking strategy to pick one property set', action='store_true')
    parser.add_argument('--no-neg', help='only use positive properties', action='store_true')
    parser.add_argument('--interactive-level', help='interact with a user. 1: run MaxSMT after users pick the properties; 2: use the properies chosen by users', type=int, choices=[1, 2])
    parser.add_argument('--auto-interaction', help='use specification function to auto choose the property', action='store_true')
    parser.add_argument('--infer-neg-by-pos', help='use positive examples to infer the negative property implicitly', action='store_true')
    parser.add_argument('--num-of-pos-example', type=int, default=1, help='the max number of positive examples returend to users')
    parser.add_argument('--num-of-neg-example', type=int, default=1, help='the max number of negative examples returend to users')
    parser.add_argument('--invert-one-pos', help='invert the only one positive property if Sketch fails to synthesize a program by it', action='store_true')
    parser.add_argument('--load-prop', help='load predefined properties from properties.conf', action='store_true')
    parser.add_argument('--only-count', help='only count the number of perturbed examples', action='store_true')
    parser.add_argument('--direct-prop', help='use properties directly', action='store_true')
    parser.add_argument('--own-generator', help='use predefined generate functions to generate examples', action='store_true')
    parser.add_argument('benchmark', help='benchmark\'s name. name+ matches name*')
    args = parser.parse_args()

    if args.directory:
        BENCHMARKS_DIR = os.path.join(BENCHMARKS_DIR, args.directory)
        ARGS_DIR.extend(args.directory.split('/'))

    if args.random:
        USE_RANDOM_EXAMPLES = True

    if args.example_nums:
        NUMS_OF_EXAMPLES = args.example_nums.split(':')

    test_type = []
    if args.test_type in ['failed',]:
        test_type = [args.test_type,]
    elif args.test_type in [ 'hard', 'soft', 'incr']:
        test_type = ['failed', args.test_type,]
    elif args.test_type == 'fixed':
        test_type = ['failed', 'hard', 'soft']

    if args.random and 'failed' not in test_type:
        test_type.append('failed')

    if args.direct_prop:
        test_type = ['prop']

    tmp_bounds = None
    if args.bound_time:
        EXAMPLE_BOUND = - args.bound_time

    if args.bound_num:
        # EXAMPLE_BOUND = args.bound_num
        tmp_bounds = args.bound_num.split(':')

    if args.just_gen:
        JUST_GEN_RAND_EXAMPLE = True

    if args.load_example:
        LOAD_EXAMPLE_FROM_FILE = True

    example_ids = []
    if args.example_id:
        example_ids = [int(x) for x in args.example_id.split(':')]

    if args.enforcement_strategy:
        ENFORCEMENT_STRATEGY = args.enforcement_strategy

    if args.default_sketch:
        USE_DEFAULT_RAW_SKETCH = True

    if args.ranking:
        USE_RANKING_STRATEGY = True

    if args.no_neg:
        PERTURBATION_PROPERTIES = perturbation.POSITIVE_PROPERTIES
        ONLY_USE_POSITIVE_PROPERTIES = True

    if args.interactive_level:
        INTERACTIVE_LEVEL = args.interactive_level

    if args.auto_interaction:
        USE_SPEC_AS_USER = True

    if args.infer_neg_by_pos:
        INFER_NEG_PROP_BY_POS_PROP = True

    if args.num_of_pos_example:
        NUM_OF_POSITIVE_EXAMPLES_TO_SHOW = args.num_of_pos_example

    if args.num_of_neg_example:
        NUM_OF_NEGATIVE_EXAMPLES_TO_SHOW = args.num_of_neg_example

    if args.invert_one_pos:
        INVERT_ONE_POSITIVE_PROP = True

    if args.load_prop:
        LOAD_PROPERTIES = True
        BENCHMARK_PROPERTY_DICT = load_ben_prop_dict()

    if args.only_count:
        ONLY_COUNTING_NUM_OF_EXAMPLES = True

    if args.own_generator:
        USE_OWN_GENERATOR = True

    benchmark_dirs = [args.benchmark, ]
    if '+' in args.benchmark:
        benchmark_dirs = [os.path.split(b)[1] for b in glob.glob(os.path.join(BENCHMARKS_DIR, args.benchmark.replace('+', '*'))) if os.path.isdir(b)]
        benchmark_dirs.sort()
        if args.range:
            s,e = args.range.split(':')
            s = int(s)
            e = int(e)
            if s < 0: s = 0
            if e > len(benchmark_dirs): e = len(benchmark_dirs)
            benchmark_dirs = benchmark_dirs[s:e]
        # benchmark_dirs = benchmark_dirs[benchmark_dirs.index('sk_src_expr_seq_thesisBenchmarks_armando_batcher_batcher_sort')+1:]

    # TODO: Ugly global var used to load the corresponding example set
    for REPEAT_INDEX in range(args.repeat):
        if example_ids and REPEAT_INDEX not in example_ids:
            continue
        if tmp_bounds is None:
            BRUTE_NEED_REMEMBER_EXAMPLES = False
            if args.random:
                for n in NUMS_OF_EXAMPLES:
                    print('Testing benchmarks with %s random example(s)' % n)
                    for benchmark_dir in benchmark_dirs:
                        test_one(benchmark_dir, test_type, int(n))
            else:
                for benchmark_dir in benchmark_dirs:
                    test_one(benchmark_dir, test_type)
        else:
            for benchmark_dir in benchmark_dirs:
                if args.random:
                    BRUTE_NEED_REMEMBER_EXAMPLES = True
                    for n in NUMS_OF_EXAMPLES:
                        BRUTE_PRESET_EXAMPLES = None
                        for tmp_bnd in tmp_bounds:
                            if args.percent:
                                EXAMPLE_BOUND = float(tmp_bnd)
                            else:
                                EXAMPLE_BOUND = int(tmp_bnd)
                            print('Testing benchmark %s with %s bounds and %s examples' % (benchmark_dir, tmp_bnd, n))
                            test_one(benchmark_dir, test_type, int(n))

                else:
                    for tmp_bnd in tmp_bounds:
                        if args.percent:
                            EXAMPLE_BOUND = float(tmp_bnd)
                        else:
                            EXAMPLE_BOUND = int(tmp_bnd)
                        print('Testing benchmarks with %s bounds' % tmp_bnd)
                        test_one(benchmark_dir, test_type)

    if ONLY_COUNTING_NUM_OF_EXAMPLES:
        print('Result of counting number of examples!')
        # for k in sorted(BEN_NUM_OF_EXAMPLES_DICT.keys()):
        #     print('%s.sk\t%s\t%s\t%s' % (k, BEN_NUM_OF_EXAMPLES_DICT[k]/args.repeat, BEN_NUM_OF_POS_EXAMPLES_DICT[k]/args.repeat, BEN_NUM_OF_NEG_EXAMPLES_DICT[k]/args.repeat))
        for k in sorted(BEN_NUM_OF_POS_EXAMPLES_DICT.keys()):
            print('%s.sk\t%s\t%s' % (k, BEN_NUM_OF_POS_EXAMPLES_DICT[k]/args.repeat, BEN_NUM_OF_NEG_EXAMPLES_DICT[k]/args.repeat))
