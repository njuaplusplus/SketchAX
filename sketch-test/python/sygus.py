#!/usr/bin/env python3
# coding=utf-8

import random
import argparse
import importlib
import re
import os
import sys
import time
import subprocess
import perturbation
import datetime
from shutil import copyfile, rmtree

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

BENCHMARKS_DIR = os.path.join(BASE_DIR, 'benchmarks')
ARGS_DIR = ['benchmarks',]

EXAMPLE_BOUND = -5 # for 10 seconds

USE_RANDOM_EXAMPLES = False

JUST_GEN_RAND_EXAMPLE = False
LOAD_EXAMPLE_FROM_FILE = False
FIXED_EXAMPLES_FILE = 'fixed_examples.txt'
REPEAT_INDEX = 0

PBE_FUNCTION_NAME = 'pbesyn'


def get_time():
    return time.perf_counter()


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


def load_example(filename, index):
    """ Load the ith example set from a file
    """
    cur = -1
    lines = []
    example_types = []
    examples = []
    num_of_exams = 3
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
                        e_ins.append([int(x) for x in e_in_s[1:-1].split(',')])
                    elif 'matrix' in e_in_type[ii]:
                        t_rows = e_in_s[2:-2].split('},{')
                        t_rows = [ [int(x) for x in r.split(',')] for r in t_rows ]
                        e_ins.append(np.array(t_rows))
                if e_out_type[0] == 'int' or e_out_type[0] == 'bit':
                    e_out = int(e_out_str)
                elif 'list' in e_out_type[0]:
                    e_out = [int(x) for x in e_out_str[1:-1].split(',')]
                elif 'matrix' in e_out_type[0]:
                    t_rows = e_out_str[2:-2].split('},{')
                    t_rows = [ [int(x) for x in r.split(',')] for r in t_rows ]
                    e_out = np.array(t_rows)
                examples.append([e_ins, [e_out]])
            break
    return example_types, examples


def get_original_constraints_code(function_name, example_types, examples):
    return perturbation.get_hard_constraints_code_helper_sygus('original', function_name, example_types, examples)[0]


def get_hard_constraints_code(hard_properties, function_name, example_types, examples, to_check_raw_sketch_output=False, need_generation=True):
    def helper(bound=0):
        # signal.signal(signal.SIGALRM, timeout_handler)
        # signal.alarm(TIME_LIMIT_FOR_CONSTRAINTS)
        codes = ''
        examples_list = []
        for prop in hard_properties:
            tmp = perturbation.get_hard_constraints_code_helper_sygus(prop, function_name, example_types, examples, bound=bound, to_check_raw_sketch_output=to_check_raw_sketch_output, need_generation=need_generation)
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


def run_test(benchmark_dir, pbe_sketch_file, function_signatures, original_code_file, output_dir, test_times=1, constraints=None, need_cmp=True):
    if constraints is not None and constraints:
        # build the sketch file first
        pbe_sketch_file = copyfile(
                pbe_sketch_file,
                os.path.join(
                    output_dir,
                    '%s_pbe_%s.sl' % (benchmark_dir,
                        datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f'))))
        with open(pbe_sketch_file, 'a') as out_file:
            out_file.write(constraints)
            out_file.write('\n(check-synth)\n')

    for _ in range(test_times):
        t1_start = get_time()
        c = subprocess.run(["/home/aplusplus/.mybuild/DryadSynth/exec.sh", pbe_sketch_file, '1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # c = subprocess.run(["/home/aplusplus/Downloads/cvc4-1.6-x86_64-linux-opt", pbe_sketch_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t1_stop = get_time()
        print('Used time: %s' % ((t1_stop-t1_start)))
        sketch_out = c.stdout.decode('utf-8')
        sketch_out = sketch_out.split('\n')[1].strip()
        print(sketch_out)
        match = re.search(r'\(define-fun\s+(\w+)\s+\(', sketch_out)
        if match and len(match.groups()) == 1:
            function_name = match.group(1)
        else:
            raise ValueError('Error: Cannot find function name %s\n' % (sketch_out, ))

        print('Found function_name: %s => %s' % (function_name, PBE_FUNCTION_NAME))

        if not need_cmp: return None

        sketch_out.replace(function_name, PBE_FUNCTION_NAME)
        cmp_code_file = os.path.join(output_dir,
                    'cmp_%s_%s.sl' % (benchmark_dir,
                        datetime.datetime.now().strftime('%Y%m%d%H%M%S.%f')))
        sk_file = original_code_file
        original_code = []
        sketch_out = sketch_out.replace(function_name, PBE_FUNCTION_NAME)
        parameters = []
        with open(sk_file) as in_file:
            original_code = in_file.read().split('\n')
        for l in original_code:
            if l.startswith('(declare-var'):
                p = l.split(' ')[1]
                parameters.append(p)
        parameters = ' '.join(parameters)
        original_code.insert(1, sketch_out)
        original_code.insert(original_code.index('(check-synth)'),
                '(constraint (= (%s %s) (%s %s)))' % (function_name, parameters, PBE_FUNCTION_NAME, parameters))
        with open(cmp_code_file, 'w') as out_file:
            out_file.write('\n'.join(original_code))

        c = subprocess.run(["/home/aplusplus/Downloads/CLIA_Track/solvers/CVC4-061117-sygus-comp-2017/bin/starexec_run_sygus_c_CLIA", cmp_code_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sketch_out = c.stdout.decode('utf-8')
        if sketch_out:
            # print(sketch_out.strip())
            print('correct')
        else:
            print('wrong')


def init_test(benchmark_dir, output_dir, pbe_sketch_file=None, original_code_file=None, example_types=None, examples=None, properties=None, hard_properties=None, number_of_examples=3):
    sk_file_dir = os.path.dirname(output_dir)
    sk_file = os.path.join(sk_file_dir, benchmark_dir+'.sl')
    original_code_file = sk_file
#     if not original_code_file:
#         original_code_file = os.path.join(sk_file_dir, benchmark_dir+'_output.sl')
#     if not os.path.isfile(original_code_file):
#         print('Synthsizing orignial code')
#         t1_start = get_time()
#         c = subprocess.run(["/home/aplusplus/.mybuild/DryadSynth/exec.sh", sk_file, '1'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#         t1_stop = get_time()
#         print('Used time: %s' % ((t1_stop-t1_start)))
#         sketch_out = c.stdout.decode('utf-8')
#         sketch_out = sketch_out.split('\n')[1].strip()
#         print(sketch_out)
#         match = re.search(r'\(define-fun\s+(\w+)\s+\(', sketch_out)
#         if match and len(match.groups()) == 1:
#             function_name = match.group(1)
#         else:
#             raise ValueError('Error: Cannot find function name %s\n' % (sketch_out, ))
# 
#         print('Found function_name:', function_name)

    if not pbe_sketch_file:
        pbe_sketch_file = os.path.join(sk_file_dir, benchmark_dir+'_pbe.sl')

    pbe_code = ''
    found_funcname = False
    maybe_in_constr = False
    with open(sk_file) as f:
        for l in f:
            l = l.strip('\n')
            if not l: continue
            if l.startswith('(constraint'):
                maybe_in_constr = True
                continue
            if maybe_in_constr:
                if l.startswith('\t') or l.startswith(' '):
                    continue
                if l.startswith(')'):
                    continue
            if l.startswith('(check-synth)') or l.startswith('(declare-var'):
                maybe_in_constr = False
                continue

            maybe_in_constr = False
            pbe_code += l + '\n'
            if not found_funcname:
                # always find the first function's name to synthesize
                match = re.search(r'\(synth-fun\s+(\w+)\s+\(', l)
                if match and len(match.groups()) == 1:
                    function_name = match.group(1)
                    found_funcname = True
                    print('Found function_name:', function_name)
        if not found_funcname:
            raise ValueError('Error: Cannot find function name\n')

    if not os.path.isfile(pbe_sketch_file):
        print('Extracting pbe code')
        with open(pbe_sketch_file, 'w') as out_file:
            out_file.write(pbe_code)

    # Check whether we need to load the examples from a file
    if LOAD_EXAMPLE_FROM_FILE:
        example_types, examples = load_example(os.path.join(sk_file_dir, FIXED_EXAMPLES_FILE), REPEAT_INDEX)
        print('Loaded %dth example set' % REPEAT_INDEX)
        print(example_types)
        print(examples)

    constraints_failed =  get_original_constraints_code(function_name, example_types, examples)
    constraints_soft_fixed = None
    constraints_hard_fixed = hard_properties and (constraints_failed + get_hard_constraints_code(hard_properties, function_name, example_types, examples)[0])

    # print(constraints_failed)
    # print(constraints_hard_fixed)

    return original_code_file, pbe_sketch_file, function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples, function_name



def test_one(benchmark_dir, test_type, number_of_examples=3):
    path = os.path.join(BENCHMARKS_DIR, benchmark_dir)
    if not os.path.isdir(path): return

    print('====== Begin Test %s ======' % benchmark_dir)
    test_config_file = os.path.join(path, 'test_config.py')
    test_times = 1
    output_dir = os.path.join(path, 'python_test')
    pbe_failed_output_dir = os.path.join(output_dir, 'failed')
    pbe_hard_fixed_output_dir = os.path.join(output_dir, 'hard_fixed')
    pbe_soft_fixed_output_dir = os.path.join(output_dir, 'soft_fixed')
    pbe_sketch_file = None
    original_code_file = None
    if not os.path.isdir(pbe_failed_output_dir):
        os.makedirs(pbe_failed_output_dir, exist_ok=True)
    if not os.path.isdir(pbe_hard_fixed_output_dir):
        os.makedirs(pbe_hard_fixed_output_dir, exist_ok=True)
    if not os.path.isdir(pbe_soft_fixed_output_dir):
        os.makedirs(pbe_soft_fixed_output_dir, exist_ok=True)
    if os.path.isfile(test_config_file):
        test_config_model = '%s.%s.test_config' % ('.'.join(ARGS_DIR), benchmark_dir)
        test_config = importlib.import_module(test_config_model)
        properties = getattr(test_config, 'properties', None)
        hard_properties = getattr(test_config, 'hard_properties', None)
        example_types = getattr(test_config, 'example_types', None)
        if USE_RANDOM_EXAMPLES or LOAD_EXAMPLE_FROM_FILE or JUST_GEN_RAND_EXAMPLE:
            examples = None
        if examples is None or not examples:
            # generate original examples
            if JUST_GEN_RAND_EXAMPLE:
                get_examples = getattr(test_config, 'get_examples', None)
                examples = get_examples and get_examples(number_of_examples)
            original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples, function_name = init_test(benchmark_dir, output_dir, pbe_sketch_file, original_code_file, example_types, examples, properties, hard_properties, number_of_examples)
    else:

        try:
            original_code_file, pbe_sketch_file, pbe_function_name, constraints_failed, constraints_hard_fixed, constraints_soft_fixed, example_types, examples, function_name = init_test(benchmark_dir, output_dir, number_of_examples=number_of_examples)
        except Exception as err:
            print("Init test error: {0}".format(err))
            # print('Deleting this benchmark')
            # comment out for incr test
            # rmtree(path)
            return

    if JUST_GEN_RAND_EXAMPLE:
        save_examples(os.path.join(path, FIXED_EXAMPLES_FILE), example_types, examples)
        return

    function_signatures = None
    if 'failed' in test_type:
        print('Test failed %s for %s times' % (pbe_sketch_file, test_times))
        try:
            run_test(benchmark_dir, pbe_sketch_file,
                function_signatures, original_code_file, pbe_failed_output_dir, test_times, constraints_failed)
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

    print('====== End Test %s ======' % benchmark_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run tests for DryadSynth benchmark')
    parser.add_argument('-d', '--directory', help='sub benchmark directory')
    parser.add_argument('-t', '--test-type', help='type of test: failed, hard, soft, incr')
    parser.add_argument('--repeat', type=int, default=1, help='times to repeat tests')
    parser.add_argument('--just-gen', help='just genearte random examples', action='store_true')
    parser.add_argument('--load-example', help='use pre-generated random examples', action='store_true')
    parser.add_argument('--no-neg', help='only use positive properties', action='store_true')
    parser.add_argument('benchmark', help='benchmark\'s name. name+ matches name*')
    args = parser.parse_args()

    if args.directory:
        BENCHMARKS_DIR = os.path.join(BENCHMARKS_DIR, args.directory)
        ARGS_DIR.extend(args.directory.split('/'))

    test_type = []
    if args.test_type in ['failed',]:
        test_type = [args.test_type,]
    elif args.test_type in [ 'hard', 'soft', 'incr']:
        test_type = ['failed', args.test_type,]
    elif args.test_type == 'fixed':
        test_type = ['failed', 'hard', 'soft']

    if args.just_gen:
        JUST_GEN_RAND_EXAMPLE = True

    if args.load_example:
        LOAD_EXAMPLE_FROM_FILE = True

    benchmark_dirs = [args.benchmark, ]

    # TODO: Ugly global var used to load the corresponding example set
    for REPEAT_INDEX in range(args.repeat):
        for benchmark_dir in benchmark_dirs:
            test_one(benchmark_dir, test_type)
