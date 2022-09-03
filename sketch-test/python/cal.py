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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

BENCHMARKS_DIR = os.path.join(BASE_DIR, 'benchmarks')
ARGS_DIR = ['benchmarks',]

TIMING = False

TIME_LIMIT_FOR_CONSTRAINTS = 5 # seconds
EXAMPLE_BOUND = -5 # for 10 seconds
NUMS_OF_EXAMPLES = [3]

USE_RANDOM_EXAMPLES = False

def get_time():
    return time.perf_counter()
    # return time.process_time()

def timeout_handler(signum, frame):
    raise Exception('Timeout for %ds!' % TIME_LIMIT_FOR_CONSTRAINTS)

def get_original_constraints_code(function_name, example_types, examples):
    return perturbation.get_hard_constraints_code_helper('original', function_name, example_types, examples)

def get_soft_constraints_code(properties, function_name, example_types, examples):
    def helper(bound=0):
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(TIME_LIMIT_FOR_CONSTRAINTS)
        codes = ''
        for prop in properties:
            get_code =  getattr(perturbation, 'get_soft_constraints_%s_code' % prop, None)
            if get_code is not None:
                codes += get_code(function_name, example_types, examples, bound=bound)
            else:
                print('Function for property %s is undefined', prop)
        # signal.alarm(0)
        return codes

    return helper(EXAMPLE_BOUND)

    # codes = ''
    # try:
    #     codes = helper()
    # except Exception as err:
    #     print('Generating soft constraints of %s has error: %s\nTry to generate with bounds %s' % (properties,err,EXAMPLE_BOUND))
    #     codes = helper(EXAMPLE_BOUND)
    # return codes


def get_hard_constraints_code(hard_properties, function_name, example_types, examples):
    def helper(bound=0):
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(TIME_LIMIT_FOR_CONSTRAINTS)
        codes = ''
        for prop in hard_properties:
            get_code =  getattr(perturbation, 'get_hard_constraints_%s_code' % prop, None)
            if get_code is not None:
                codes += get_code(function_name, example_types, examples, bound=bound)
            else:
                print('Hard constraints function for property %s is undefined' % prop)
        # signal.alarm(0)
        return codes

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
            raise ValueError('Cannot get the total time')
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
                end_index = sketch_out.index('\n}\n', start_index+1)
                original_code = sketch_out[start_index:end_index+3]
            except ValueError:
                try:
                    # The synthesized function is empty
                    end_index = sketch_out.index('\n{ }\n', start_index+1)
                    original_code = sketch_out[start_index:end_index+5]
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
        raise ValueError('this function has no input')
    if len(example_types[0]) == 1 and example_types[0][0] == 'bit':
        raise ValueError('this function has only a bit input')
    if example_types[1][0] == 'void':
        raise ValueError('this function has no output')
    constraints_failed =  get_original_constraints_code(pbe_function_name, example_types, examples)
    constraints_soft_fixed = None
    if properties:
        print('------ Begin get_soft_constraints_code for %s ------' % properties)
        t1_start = get_time()
        tmp_cons = get_soft_constraints_code(properties, pbe_function_name, example_types, examples)
        t1_stop = get_time()
        print('Used time: %s' % ((t1_stop-t1_start)))
        constraints_soft_fixed = constraints_failed + tmp_cons
        print('------ End get_soft_constraints_code ------')
    # TODO: remove
    # constraints_hard_fixed = hard_properties and (constraints_failed + get_hard_constraints_code(hard_properties, pbe_function_name, example_types, examples))
    constraints_hard_fixed = ''
    t_num_of_e = 0
    if hard_properties:
        for p in hard_properties:
            constraints_hard_fixed = get_hard_constraints_code([p,], pbe_function_name, example_types, examples)
            t_num_of_e += len(constraints_hard_fixed.split('\n')) - 3
        print("|E'| for %s is %d" % (benchmark_dir, t_num_of_e))


    return original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples

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
        raise ValueError('Cannot get the total time')
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

def incremental_test(benchmark_dir, pbe_sketch_file, original_code_file, output_dir, pbe_function_name, example_types, examples):
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

    function_signatures = [ 'void '+ pbe_function_name ]
    test_times = 1
    candidate_properties = []
    applicable_properties = []
    prop_soft_constr_dict = {}
    hard_constraints =  get_original_constraints_code(pbe_function_name, example_types, examples)
    tmp_output_dir = os.path.join(output_dir, '1')
    if not os.path.isdir(tmp_output_dir):
        os.makedirs(tmp_output_dir, exist_ok=True)
    print('------ Begin get_soft_constraints_code for %s ------' % perturbation.properties)
    t1_start = get_time()
    for prop in perturbation.properties:
        try:
            tmp = get_soft_constraints_code([prop,], pbe_function_name, example_types, examples)
            if tmp:
                prop_soft_constr_dict[prop] = tmp
                applicable_properties.append(prop)
        except Exception as err:
            print('Generating soft constraints of %s has error: %s' % (prop,err))
    # compute the number of E'
    t_num_of_e = 0
    for p in prop_soft_constr_dict:
        t_num_of_e += len(prop_soft_constr_dict[p].split('\n')) - 5
    print("|E'| for %s is %d" % (benchmark_dir, t_num_of_e))
    return

    t1_stop = get_time()
    print('Used time: %s' % ((t1_stop-t1_start)))
    print('------ End get_soft_constraints_code ------')
    for prop in applicable_properties:
        soft_constraints = prop_soft_constr_dict[prop]
        print('Trying properties:', prop)
        try:
            run_test(benchmark_dir, pbe_sketch_file,
                    function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)
        except ValueError as err:
            #print("Run test error: {0}".format(err))
            pass
        else:
            candidate_properties.append(prop)

    tmp_output_dir = os.path.join(output_dir, 'result')
    if not os.path.isdir(tmp_output_dir):
        os.makedirs(tmp_output_dir, exist_ok=True)
    if len(candidate_properties) == 0:
        print('No applicable property, so only use user-provided examples')
        try:
            run_test(benchmark_dir, pbe_sketch_file,
                    function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints)
        except ValueError as err:
            #print("Run test error: {0}".format(err))
            return
    elif len(candidate_properties) == 1:
        prop = candidate_properties[0]
        print('Using property:', prop)
        soft_constraints = prop_soft_constr_dict[prop]
        try:
            run_test(benchmark_dir, pbe_sketch_file,
                    function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)
        except ValueError as err:
            #print("Run test error: {0}".format(err))
            return
    else:
        current_property_sets = [[p,] for p in candidate_properties]
        conflict_property_dict = {}
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
                        run_test(benchmark_dir, pbe_sketch_file,
                                function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)
                    except ValueError as err:
                        # print("Run test error: {0}".format(err))
                        # print('updating conflict', tmp_prop_set)
                        if len(tmp_prop_set) == 2: update_conflicts(conflict_property_dict, tmp_prop_set[0], tmp_prop_set[1])
                    else:
                        new_current_property_set.append(tmp_prop_set)
            if len(new_current_property_set) == 0:
                # use the current property set in the last iteration
                break
            current_property_sets = new_current_property_set[:]

        tmp_output_dir = os.path.join(output_dir, 'result')
        if not os.path.isdir(tmp_output_dir):
            os.makedirs(tmp_output_dir, exist_ok=True)
        if len(current_property_sets) == 0:
            print('No applicable property, so only use user-provided examples')
            try:
                run_test(benchmark_dir, pbe_sketch_file,
                        function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints)
            except ValueError as err:
                #print("Run test error: {0}".format(err))
                return
        elif len(current_property_sets) >= 1:
            props = current_property_sets[0]
            print('Using properties:', props)
            soft_constraints = ''.join([prop_soft_constr_dict[p] for p in props])
            try:
                run_test(benchmark_dir, pbe_sketch_file,
                        function_signatures, original_code_file, tmp_output_dir, test_times, hard_constraints + soft_constraints)
            except ValueError as err:
                #print("Run test error: {0}".format(err))
                return
        else:
            print('Error! This error should not happen!')

def run_test(benchmark_dir, pbe_sketch_file, function_signatures, original_code_file, output_dir, test_times=1, constraints=None):
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
        c = subprocess.run(["sketch", "--slv-seed", "7", "--fe-timeout", "5", pbe_sketch_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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
            raise ValueError('Cannot get the total time')
        for f in function_signatures:
            try:
                start_index = sketch_out.index(f)
            except ValueError:
                print('Can not find function %s from\n%s' % (f, sketch_out))
                raise
            try:
                end_index = sketch_out.index('\n}\n', start_index+1)
                tmp_code = sketch_out[start_index:end_index+3]
            except ValueError:
                try:
                    # The synthesized function is empty
                    end_index = sketch_out.index('\n{ }\n', start_index+1)
                    tmp_code = sketch_out[start_index:end_index+5]
                except ValueError:
                    #print('Can not find the end of the function %s from\n%s' % (f, sketch_out))
                    raise
            if 'implements' in tmp_code:
                print('Find implements in tmp_code!')
                s1 = tmp_code.index('implements')
                s2 = tmp_code.index('\n', s1+1)
                tmp_code = tmp_code[:s1] + tmp_code[s2:]
            synthesized_code += tmp_code

        cmp_code_file = copyfile(
                original_code_file,
                os.path.join(
                    output_dir,
                    'cmp_%s_%s.sk' % (benchmark_dir,
                        datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'))))
        with open(cmp_code_file, 'a') as out_file:
            out_file.write(synthesized_code)

        c = subprocess.run(["sketch", "--fe-timeout", "5", cmp_code_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        cmp_result = c.stdout.decode('utf-8')
        cmp_result_file = cmp_code_file + '.output'
        total_time = 0
        match = re.search(r'Total time = (\d+)', cmp_result)
        if match and len(match.groups()) > 0:
            total_time = match.group(1)
            print('Total time:', total_time)
        else:
            raise ValueError('Cannot get the total time')
        if 'UNSATISFIABLE' in cmp_result or 'Rejected' in cmp_result:
            cmp_result_file += '.wrong'
        elif 'front-end timed out' in cmp_result:
            cmp_result_file += '.check'
            print('Sketch timeout! Please check this file manually %s' % cmp_code_file)
        else:
            cmp_result_file += '.right'
            cnt_right += 1

        with open(cmp_result_file, 'a') as out_file:
            out_file.write(cmp_result)
    #print('using constraints:\n', constraints)
    print('right rate: %d / %d' % (cnt_right, test_times))

def test_all(test_type):
    for benchmark_dir in os.listdir(BENCHMARKS_DIR):
        test_one(benchmark_dir, test_type)

def test_one(benchmark_dir, test_type, number_of_examples=3):
    print('====== Begin Test %s ======' % benchmark_dir)
    path = os.path.join(BENCHMARKS_DIR, benchmark_dir)
    if not os.path.isdir(path): return
    test_config_file = os.path.join(path, 'test_config.py')
    function_signatures = None
    test_times = 1
    output_dir = os.path.join(path, 'python_test')
    pbe_failed_output_dir = os.path.join(output_dir, 'failed')
    pbe_hard_fixed_output_dir = os.path.join(output_dir, 'hard_fixed')
    pbe_soft_fixed_output_dir = os.path.join(output_dir, 'soft_fixed')
    if not os.path.isdir(pbe_failed_output_dir):
        os.makedirs(pbe_failed_output_dir, exist_ok=True)
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
        if USE_RANDOM_EXAMPLES:
            examples = None
        # TODO: remove
        print("|E| for %s is %d" % (benchmark_dir, len(examples)))
        if examples is None or not examples:
            # generate original examples
            if USE_RANDOM_EXAMPLES:
                get_examples = getattr(test_config, 'get_examples', None)
                examples = get_examples and get_examples(number_of_examples)
            # constraints_failed = test_config.get_original_constraints_code(examples)
            original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples = init_test(benchmark_dir, output_dir, pbe_sketch_file, original_code_file, example_types, examples, properties, hard_properties, number_of_examples)
        else:
            pbe_function_name = getattr(test_config, 'function_name', None)
            if pbe_function_name is None:
                original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples = init_test(benchmark_dir, output_dir, pbe_sketch_file, original_code_file, example_types, examples, properties, hard_properties, number_of_examples)
            else:
                constraints_failed = get_original_constraints_code(pbe_function_name, example_types, examples)
                constraints_soft_fixed = None
                if 'soft' in test_type and properties:
                    print('------ Begin get_soft_constraints_code for %s ------' % properties)
                    t1_start = get_time()
                    tmp_cons = get_soft_constraints_code(properties, pbe_function_name, example_types, examples)
                    t1_stop = get_time()
                    print('Used time: %s' % ((t1_stop-t1_start)))
                    constraints_soft_fixed = constraints_failed + tmp_cons
                    print('------ End get_soft_constraints_code ------')
                if 'hard' in test_type:
                    constraints_hard_fixed = hard_properties and (constraints_failed + get_hard_constraints_code(hard_properties, pbe_function_name, example_types, examples))
    else:
        try:
            original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples = init_test(benchmark_dir, output_dir, number_of_examples=number_of_examples)
        except Exception as err:
            print("Init test error: {0}".format(err))
            # print('Deleting this benchmark')
            # comment out for incr test
            # rmtree(path)
            return
    if function_signatures is None:
        function_signatures = [ 'void '+ pbe_function_name ]

#    if 'failed' in test_type:
#        print('Test failed %s for %s times' % (pbe_sketch_file, test_times))
#        try:
#            run_test(benchmark_dir, pbe_sketch_file,
#                function_signatures, original_code_file, pbe_failed_output_dir, test_times, constraints_failed)
#        except ValueError as err:
#            print("Run test error: {0}".format(err))
#            # print('Deleting this benchmark')
#            # rmtree(path)
#            return
#    if 'hard' in test_type:
#        if constraints_hard_fixed:
#            print('Test hard fixed %s for %s times' % (pbe_sketch_file, test_times))
#            try:
#                run_test(benchmark_dir, pbe_sketch_file,
#                        function_signatures, original_code_file, pbe_hard_fixed_output_dir, test_times, constraints_hard_fixed)
#            except ValueError as err:
#                print("Run test error: {0}".format(err))
#                # print('Deleting this benchmark')
#                # rmtree(path)
#                return
#    if 'soft' in test_type:
#        if constraints_soft_fixed:
#            print('Test soft fixed %s for %s times' % (pbe_sketch_file, test_times))
#            try:
#                run_test(benchmark_dir, pbe_sketch_file,
#                        function_signatures, original_code_file, pbe_soft_fixed_output_dir, test_times, constraints_soft_fixed)
#            except ValueError as err:
#                print("Run test error: {0}".format(err))
#                # print('Deleting this benchmark')
#                # rmtree(path)
#                return
    if 'incr' in test_type:
        print('Test incrementally %s for %s times' % (pbe_sketch_file, test_times))
        inc_output_dir = os.path.join(output_dir, 'inc')
        if not os.path.isdir(inc_output_dir):
            os.makedirs(inc_output_dir)
        try:
            incremental_test(benchmark_dir, pbe_sketch_file, original_code_file, inc_output_dir, pbe_function_name, example_types, examples)
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
    parser.add_argument('--bound-num', type=int, help='bound the number of examples by 256 by default')
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

    if args.bound_time:
        EXAMPLE_BOUND = - args.bound_time

    if args.bound_num:
        EXAMPLE_BOUND = args.bound_num

    benchmark_dirs = [args.benchmark, ]
    if '+' in args.benchmark:
        benchmark_dirs = [os.path.split(b)[1] for b in glob.glob(os.path.join(BENCHMARKS_DIR, args.benchmark.replace('+', '*')))]
        benchmark_dirs.sort()
        if args.range:
            s,e = args.range.split(':')
            s = int(s)
            e = int(e)
            if s < 0: s = 0
            if e > len(benchmark_dirs): e = len(benchmark_dirs)
            benchmark_dirs = benchmark_dirs[s:e]
        # benchmark_dirs = benchmark_dirs[benchmark_dirs.index('sk_src_expr_seq_thesisBenchmarks_armando_batcher_batcher_sort')+1:]

    for _ in range(args.repeat):
        if args.random:
            for n in NUMS_OF_EXAMPLES:
                print('Testing benchmarks with %s random example(s)' % n)
                for benchmark_dir in benchmark_dirs:
                    test_one(benchmark_dir, test_type, int(n))
        else:
            for benchmark_dir in benchmark_dirs:
                test_one(benchmark_dir, test_type)
