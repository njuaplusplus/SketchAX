#!/usr/bin/env python
# coding=utf-8
import numpy as np
import itertools
import random
import time
import math
import functools

BOUND_OF_NUM_OF_EXAMPLES = 512
EXTRA_SAMPLING_TIMES = 20
BOUND_OF_NUM_OF_EACH_EXAMPLE = 128
BOUND_OF_K = 100
DEFAULT_NUM_OF_K = 5
DEFAULT_BOUND_OF_TIME = -5 # Same to example_bound, brute-force solution for bound 1000+x for permutation

DEFAULT_K = 10
# some times K = 1 is sufficient


def get_time():
    return time.perf_counter()

def get_constraints_code(examples, get_an_assertion):
    code = ''
    for example in examples:
        code += get_an_assertion(example)
    return 'harness void hard_constraints() {\n%s}\n' % code

class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences

def perm_unique(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    u=len(elements)
    return perm_unique_helper(listunique,[0]*u,u-1)

def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1

def get_ks(bound, is_mult=False):
    if bound <= 1000:
        # By default, randomly choose DEFAULT_NUM_OF_K ks
        # But we now return range(10) or range(1,10)
        # bound = DEFAULT_NUM_OF_K
        if is_mult:
            return range(2, DEFAULT_K+1)
        else:
            return range(1, DEFAULT_K+1)
    else:
        bound = int(bound) % 1000
        if bound > BOUND_OF_K:
            bound = DEFAULT_NUM_OF_K
    if is_mult:
        l = range(2, BOUND_OF_K+1)
    else:
        l = range(1, BOUND_OF_K+1)
    return random.sample(l, bound)

def total_num_of_permutations(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    num = math.factorial(len(elements))
    for i in listunique:
        num /= math.factorial(i.occurrences)
    return num

def get_bound(bound, e_ins, input_types, maxtrix_by_row=False):
    """Get the bound for each input example e_in
    """
    if bound < 0 or bound > 1: return min(bound, BOUND_OF_NUM_OF_EACH_EXAMPLE)
    list_list = [e_in for i,e_in in enumerate(e_ins) if input_types[i] == list or 'list' in input_types[i]]
    if not list_list:
        matrix_list = [e_in for i,e_in in enumerate(e_ins) if 'matrix' in input_types[i]]
        if maxtrix_by_row:
            matrix_list = [[','.join([str(x) for x in row]) for row in mat] for mat in matrix_list]
        else:
            matrix_list = [mat.flatten().tolist() for mat in matrix_list]
        list_list = matrix_list
    total_num = max((
        total_num_of_permutations(e_in) for e_in in list_list
    ))
    return min(math.ceil(total_num * bound), BOUND_OF_NUM_OF_EACH_EXAMPLE)

def generate_permutation_invariant_examples(example_types, examples, bound=0, positive_prop=True):
    if bound > 1000: bound = DEFAULT_BOUND_OF_TIME
    input_types, output_types = example_types

    duplicate = {}
    generated_examples = []

    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    bound_seconds = 0
    if bound < 0:
        bound_seconds = -bound

    for example in examples:
        e_ins, e_out = example
        e_ins_str = str(e_ins)
        e_out_str = str(e_out)
        if e_ins_str in duplicate:
            if e_out_str not in duplicate[e_ins_str]:
                if positive_prop:
                    # we find some incompatible examples, so this positive property can not be hold
                    return []
            else:
                # exactly same input-output examples and skip this one
                continue
        else:
            duplicate[e_ins_str] = [e_out_str]

        list_size = get_list_size(example_types, example, only_input=True)
        if list_size == 0:
            # none of the input/output contains a list
            return None
            # generated_examples.append([e_ins, e_out])
        # generate the permutations of indices
        # permute all lists with same permutation of indices
        if bound <= 0:
            num_of_gened_examples = 0
            start_time = get_time()
            print('bound time', bound_seconds)
            # generate all the perumutations
            for indices in itertools.permutations(range(list_size)):
                if bound_seconds:
                    stop_time = get_time()
                    if stop_time-start_time > bound_seconds:
                        print('Running out of time %s' % bound_seconds)
                        print('Got %s perturbed examples' % num_of_gened_examples)
                        break
                if num_of_gened_examples == BOUND_OF_NUM_OF_EACH_EXAMPLE:
                    print('Enough number for this example %s' % BOUND_OF_NUM_OF_EACH_EXAMPLE)
                    break
                e_ins_p = []
                for i in range(len(e_ins)):
                    e_in = e_ins[i]
                    if input_types[i] == list or 'list' in input_types[i]:
                        e_in_p = []
                        for index in indices:
                            e_in_p.append(e_in[index])
                    else:
                        e_in_p = e_in
                    e_ins_p.append(e_in_p)
                e_ins_p_str = str(e_ins_p)
                e_out_str = str(e_out)
                if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_out_str:
                    # same with some user-provided example, so skip
                    continue
                if e_ins_p_str in duplicate:
                    if e_out_str not in duplicate[e_ins_p_str]:
                        if positive_prop:
                            # we find some incompatible examples, so this positive property can not be hold
                            return []
                    else:
                        # exactly same input-output examples and skip this one
                        continue
                else:
                    duplicate[e_ins_p_str] = []
                duplicate[e_ins_p_str].append(e_out_str)
                num_of_gened_examples += 1
                generated_examples.append([e_ins_p, e_out])
        else:
            real_bound = get_bound(bound, e_ins, input_types)
            l_bound = real_bound + EXTRA_SAMPLING_TIMES
            indices = list(range(list_size))
            tmp_gen_exam = []
            while len(tmp_gen_exam) < real_bound and l_bound > 0:
                l_bound -= 1
                random.shuffle(indices)
                e_ins_p = []
                for i in range(len(e_ins)):
                    e_in = e_ins[i]
                    if input_types[i] == list or 'list' in input_types[i]:
                        e_in_p = []
                        for index in indices:
                            e_in_p.append(e_in[index])
                    else:
                        e_in_p = e_in
                    e_ins_p.append(e_in_p)
                e_ins_p_str = str(e_ins_p)
                e_out_str = str(e_out)
                if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_out_str:
                    # same with some user-provided example, so skip
                    continue
                if e_ins_p_str in duplicate:
                    if e_out_str not in  duplicate[e_ins_p_str]:
                        if positive_prop:
                            # we find some incompatible examples, so this positive property can not be hold
                            return []
                    else:
                        # exactly same input-output examples and skip this one
                        continue
                else:
                    duplicate[e_ins_p_str] = []
                duplicate[e_ins_p_str].append(e_out_str)
                tmp_gen_exam.append([e_ins_p, e_out])
            generated_examples.extend(tmp_gen_exam)
    return generated_examples

def generate_permutation_permutation_examples(example_types, examples, bound=0, positive_prop=True):
    if bound > 1000: bound = DEFAULT_BOUND_OF_TIME
    input_types, output_types = example_types

    duplicate = {}
    generated_examples = []


    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    bound_seconds = 0
    if bound < 0:
        bound_seconds = -bound

    for example in examples:
        e_ins, e_outs = example
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]

        list_size = get_list_size(example_types, example)
        if list_size != 0:
            if bound <= 0:
                num_of_gened_examples = 0
                start_time = get_time()
                print('bound time', bound_seconds)
                # generate the permutations of indices
                # permute all lists with same permutation of indices
                for indices in itertools.permutations(range(list_size)):
                    if bound_seconds:
                        stop_time = get_time()
                        if stop_time-start_time > bound_seconds:
                            print('Running out of time %s' % bound_seconds)
                            print('Got %s perturbed examples' % num_of_gened_examples)
                            break
                    if num_of_gened_examples == BOUND_OF_NUM_OF_EACH_EXAMPLE:
                        print('Enough number for this example %s' % BOUND_OF_NUM_OF_EACH_EXAMPLE)
                        break
                    e_ins_p = []
                    for i in range(len(e_ins)):
                        e_in = e_ins[i]
                        if input_types[i] == list or 'list' in input_types[i]:
                            e_in_p = []
                            for index in indices:
                                e_in_p.append(e_in[index])
                        else:
                            e_in_p = e_in
                        e_ins_p.append(e_in_p)
                    e_outs_p = []
                    for i, e_out in enumerate(e_outs):
                        if output_types[i] == list or 'list' in output_types[i]:
                            e_out_p = []
                            for index in indices:
                                e_out_p.append(e_out[index])
                        else:
                            e_out_p = e_out
                        e_outs_p.append(e_out_p)
                    e_ins_p_str = str(e_ins_p)
                    e_outs_p_str = str(e_outs_p)
                    if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                        # same with some user-provided example, so skip
                        continue
                    if e_ins_p_str in duplicate:
                        if e_outs_p_str not in duplicate[e_ins_p_str]:
                            if positive_prop:
                                return []
                        else:
                            continue
                    else:
                        duplicate[e_ins_p_str] = []
                    duplicate[e_ins_p_str].append(e_outs_p_str)
                    num_of_gened_examples += 1
                    generated_examples.append([e_ins_p, e_outs_p])
            else:
                real_bound = get_bound(bound, e_ins, input_types)
                l_bound = real_bound + EXTRA_SAMPLING_TIMES
                indices = list(range(list_size))
                tmp_gen_exam = []
                while len(tmp_gen_exam) < real_bound and l_bound > 0:
                    l_bound -= 1
                    random.shuffle(indices)
                    e_ins_p = []
                    for i in range(len(e_ins)):
                        e_in = e_ins[i]
                        if input_types[i] == list or 'list' in input_types[i]:
                            e_in_p = []
                            for index in indices:
                                e_in_p.append(e_in[index])
                        else:
                            e_in_p = e_in
                        e_ins_p.append(e_in_p)
                    e_outs_p = []
                    for i, e_out in enumerate(e_outs):
                        if output_types[i] == list or 'list' in output_types[i]:
                            e_out_p = []
                            for index in indices:
                                e_out_p.append(e_out[index])
                        else:
                            e_out_p = e_out
                        e_outs_p.append(e_out_p)
                    e_ins_p_str = str(e_ins_p)
                    e_outs_p_str = str(e_outs_p)
                    if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                        # same with some user-provided example, so skip
                        continue
                    if e_ins_p_str in duplicate:
                        if e_outs_p_str not in duplicate[e_ins_p_str]:
                            if positive_prop:
                                return []
                        else:
                            continue
                    else:
                        duplicate[e_ins_p_str] = []
                    duplicate[e_ins_p_str].append(e_outs_p_str)
                    tmp_gen_exam.append([e_ins_p, e_outs_p])
                generated_examples.extend(tmp_gen_exam)
        else:
            matrix_shape = get_matrix_shape(example_types, example)
            if matrix_shape != (0,0):
                # same permutation without considering rows or columns
                flatten_size = matrix_shape[0] * matrix_shape[1]
                if bound <= 0:
                    num_of_gened_examples = 0
                    start_time = get_time()
                    print('bound time', bound_seconds)
                    for indices in itertools.permutations(range(flatten_size)):
                        if bound_seconds:
                            stop_time = get_time()
                            if stop_time-start_time > bound_seconds:
                                print('Running out of time %s' % bound_seconds)
                                print('Got %s perturbed examples' % num_of_gened_examples)
                                break
                        if num_of_gened_examples == BOUND_OF_NUM_OF_EACH_EXAMPLE:
                            print('Enough number for this example %s' % BOUND_OF_NUM_OF_EACH_EXAMPLE)
                            break
                        e_ins_p = []
                        for i, e_in in enumerate(e_ins):
                            if 'matrix' in input_types[i]:
                                e_in = e_in.flatten()
                                e_in_p = e_in[list(indices)].reshape(matrix_shape)
                            else:
                                e_in_p = e_in
                            e_ins_p.append(e_in_p)
                        e_outs_p = []
                        for i, e_out in enumerate(e_outs):
                            if 'matrix' in output_types[i]:
                                e_out = e_out.flatten()
                                e_out_p = e_out[list(indices)].reshape(matrix_shape)
                            else:
                                e_out_p = e_out
                            e_outs_p.append(e_out_p)
                        e_ins_p_str = str(e_ins_p)
                        e_outs_p_str = str(e_outs_p)
                        if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                            # same with some user-provided example, so skip
                            continue
                        if e_ins_p_str in duplicate:
                            if e_outs_p_str not in duplicate[e_ins_p_str]:
                                if positive_prop:
                                    return []
                            else:
                                continue
                        else:
                            duplicate[e_ins_p_str] = []
                        duplicate[e_ins_p_str].append(e_outs_p_str)
                        generated_examples.append([e_ins_p, e_outs_p])
                else:
                    real_bound = get_bound(bound, e_ins, input_types)
                    l_bound = real_bound + EXTRA_SAMPLING_TIMES
                    indices = list(range(flatten_size))
                    tmp_gen_exam = []
                    while len(tmp_gen_exam) < real_bound and l_bound > 0:
                        l_bound -= 1
                        random.shuffle(indices)
                        e_ins_p = []
                        for i, e_in in enumerate(e_ins):
                            if 'matrix' in input_types[i]:
                                e_in = e_in.flatten()
                                e_in_p = e_in[list(indices)].reshape(matrix_shape)
                            else:
                                e_in_p = e_in
                            e_ins_p.append(e_in_p)
                        e_outs_p = []
                        for i, e_out in enumerate(e_outs):
                            if 'matrix' in output_types[i]:
                                e_out = e_out.flatten()
                                e_out_p = e_out[list(indices)].reshape(matrix_shape)
                            else:
                                e_out_p = e_out
                            e_outs_p.append(e_out_p)
                        e_ins_p_str = str(e_ins_p)
                        e_outs_p_str = str(e_outs_p)
                        if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                            # same with some user-provided example, so skip
                            continue
                        if e_ins_p_str in duplicate:
                            if e_outs_p_str not in duplicate[e_ins_p_str]:
                                if positive_prop:
                                    return []
                            else:
                                continue
                        else:
                            duplicate[e_ins_p_str] = []
                        duplicate[e_ins_p_str].append(e_outs_p_str)
                        tmp_gen_exam.append([e_ins_p, e_outs_p])
                    generated_examples.extend(tmp_gen_exam)
            else:
                list_size = get_list_size(example_types, example, only_input=True)
                if 'list' in output_types[0] and len(example[0]) == 2 and 'list' in input_types[0] and 'list' in input_types[1] and len(example[1][0]) == 2*list_size:
                    # might interleave the two inputs
                    pass
                    if bound <= 0:
                        num_of_gened_examples = 0
                        start_time = get_time()
                        print('bound time', bound_seconds)
                        # generate the permutations of indices
                        # permute all lists with same permutation of indices
                        for indices in itertools.permutations(range(list_size)):
                            if bound_seconds:
                                stop_time = get_time()
                                if stop_time-start_time > bound_seconds:
                                    print('Running out of time %s' % bound_seconds)
                                    print('Got %s perturbed examples' % num_of_gened_examples)
                                    break
                            if num_of_gened_examples == BOUND_OF_NUM_OF_EACH_EXAMPLE:
                                print('Enough number for this example %s' % BOUND_OF_NUM_OF_EACH_EXAMPLE)
                                break
                            e_ins_p = []
                            for i in range(len(e_ins)):
                                e_in = e_ins[i]
                                if input_types[i] == list or 'list' in input_types[i]:
                                    e_in_p = []
                                    for index in indices:
                                        e_in_p.append(e_in[index])
                                else:
                                    e_in_p = e_in
                                e_ins_p.append(e_in_p)
                            e_outs_p = []
                            for i, e_out in enumerate(e_outs):
                                if output_types[i] == list or 'list' in output_types[i]:
                                    e_out_p = []
                                    for index in indices:
                                        e_out_p.append(e_out[2*index])
                                        e_out_p.append(e_out[2*index+1])
                                else:
                                    e_out_p = e_out
                                e_outs_p.append(e_out_p)
                            e_ins_p_str = str(e_ins_p)
                            e_outs_p_str = str(e_outs_p)
                            if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                                # same with some user-provided example, so skip
                                continue
                            if e_ins_p_str in duplicate:
                                if e_outs_p_str not in duplicate[e_ins_p_str]:
                                    if positive_prop:
                                        return []
                                else:
                                    continue
                            else:
                                duplicate[e_ins_p_str] = []
                            duplicate[e_ins_p_str].append(e_outs_p_str)
                            num_of_gened_examples += 1
                            generated_examples.append([e_ins_p, e_outs_p])
                    else:
                        real_bound = get_bound(bound, e_ins, input_types)
                        l_bound = real_bound + EXTRA_SAMPLING_TIMES
                        indices = list(range(list_size))
                        tmp_gen_exam = []
                        while len(tmp_gen_exam) < real_bound and l_bound > 0:
                            l_bound -= 1
                            random.shuffle(indices)
                            e_ins_p = []
                            for i in range(len(e_ins)):
                                e_in = e_ins[i]
                                if input_types[i] == list or 'list' in input_types[i]:
                                    e_in_p = []
                                    for index in indices:
                                        e_in_p.append(e_in[index])
                                else:
                                    e_in_p = e_in
                                e_ins_p.append(e_in_p)
                            e_outs_p = []
                            for i, e_out in enumerate(e_outs):
                                if output_types[i] == list or 'list' in output_types[i]:
                                    e_out_p = []
                                    for index in indices:
                                        e_out_p.append(e_out[2*index])
                                        e_out_p.append(e_out[2*index+1])
                                else:
                                    e_out_p = e_out
                                e_outs_p.append(e_out_p)
                            e_ins_p_str = str(e_ins_p)
                            e_outs_p_str = str(e_outs_p)
                            if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                                # same with some user-provided example, so skip
                                continue
                            if e_ins_p_str in duplicate:
                                if e_outs_p_str not in duplicate[e_ins_p_str]:
                                    if positive_prop:
                                        return []
                                else:
                                    continue
                            else:
                                duplicate[e_ins_p_str] = []
                            duplicate[e_ins_p_str].append(e_outs_p_str)
                            tmp_gen_exam.append([e_ins_p, e_outs_p])
                        generated_examples.extend(tmp_gen_exam)
                else:
                    # none of the input/output contains a list
                    # no need to permute
                    return None
    return generated_examples


def k_uniform_add(arr, k):
    if isinstance(arr, (list, tuple)):
        return [x+k for x in arr]
    if isinstance(arr, int):
        return arr+k
    if isinstance(arr, np.ndarray):
        return arr+k
    return arr

def generate_k_uniform_add_k_examples(example_types, examples, bound=0, positive_prop=True):
    input_types, output_types = example_types
    # exclude the inputs only consisting of bit
    need_exclude = False
    for in_type in input_types:
        # allow bit to remain unchanged in the generated examples
        # if 'bit' in in_type:
        #     return None
        # TODO: brute fix for char
        if 'char' in in_type:
            return None
    if need_exclude: return None
    duplicate = {}
    generated_examples = []

    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]

        #for k in range(K+1):
        for k in get_ks(bound):
            e_ins_k = []
            for i,e_in in enumerate(e_ins):
                e_in_k = e_in
                if 'bit' not in input_types[i] and input_types[i] != 'int_N':
                    e_in_k = k_uniform_add(e_in, k)
                e_ins_k.append(e_in_k)
            e_outs_k = []
            for i,e_out in enumerate(e_outs):
                e_out_k = e_out
                if 'bit' not in output_types[i] and output_types[i] != 'int_N':
                    e_out_k = k_uniform_add(e_out, k)
                e_outs_k.append(e_out_k)
            e_ins_k_str = str(e_ins_k)
            e_outs_k_str = str(e_outs_k)
            if e_ins_k_str in original_examples_dict and original_examples_dict[e_ins_k_str] == e_outs_k_str:
                # same with some user-provided example, so skip
                continue
            if e_ins_k_str in duplicate:
                if e_outs_k_str not in duplicate[e_ins_k_str]:
                    if positive_prop:
                        return []
                else:
                    continue
            else:
                duplicate[e_ins_k_str] = []
            duplicate[e_ins_k_str].append(e_outs_k_str)
            generated_examples.append([e_ins_k, e_outs_k])
    return generated_examples


def generate_k_uniform_add_invariant_examples(example_types, examples, bound=0, positive_prop=True):
    input_types, output_types = example_types
    # exclude the inputs only consisting of bit
    need_exclude = False
    for in_type in input_types:
        # allow bit to remain unchanged in the generated examples
        # if 'bit' in in_type:
        #     return None
        # TODO: brute fix for char
        if 'char' in in_type:
            return None
    if need_exclude: return None
    duplicate = {}
    generated_examples = []

    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]

        #for k in range(K+1):
        for k in get_ks(bound):
            e_ins_k = []
            for i,e_in in enumerate(e_ins):
                e_in_k = e_in
                if 'bit' not in input_types[i] and input_types[i] != 'int_N':
                    e_in_k = k_uniform_add(e_in, k)
                e_ins_k.append(e_in_k)
            e_outs_k = []
            for i,e_out in enumerate(e_outs):
                e_out_k = e_out
                e_outs_k.append(e_out_k)
            e_ins_k_str = str(e_ins_k)
            e_outs_k_str = str(e_outs_k)
            if e_ins_k_str in original_examples_dict and original_examples_dict[e_ins_k_str] == e_outs_k_str:
                # same with some user-provided example, so skip
                continue
            if e_ins_k_str in duplicate:
                if e_outs_k_str not in duplicate[e_ins_k_str]:
                    if positive_prop:
                        return []
                else:
                    continue
            else:
                duplicate[e_ins_k_str] = []
            duplicate[e_ins_k_str].append(e_outs_k_str)
            generated_examples.append([e_ins_k, e_outs_k])
    return generated_examples


# deprecated, outdated
def generate_k1_k2_uniform_add_k1_k2_examples(example_types, examples, bound=0, positive_prop=True):
    duplicate = []
    generated_examples = []

    # This works for programs which take in two array inputs.

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        for k1 in range(K+1):
            for k2 in range(K+1):
                e_ins_k = [k_uniform_add(e_ins[0], k1), k_uniform_add(e_ins[1], k2)]
                e_ins_k_str = str(e_ins_k)
                if e_ins_k_str in duplicate:
                    continue
                duplicate.append(e_ins_k_str)
                e_outs_k = [k_uniform_add(e_outs[0], k1+k2)]
                generated_examples.append([e_ins_k, e_outs_k])
    return generated_examples


def k_uniform_mult(arr, k):
    if isinstance(arr, (list, tuple)):
        return [x*k for x in arr]
    if isinstance(arr, int):
        return arr*k
    if isinstance(arr, np.ndarray):
        return arr*k
    return arr

def generate_k_uniform_mult_k_examples(example_types, examples, bound=0, positive_prop=True):
    input_types, output_types = example_types
    need_exclude = False
    for in_type in input_types:
        # allow bit to remain unchanged in the generated examples
        # if 'bit' in in_type:
        #     return None
        # TODO: brute fix for char
        if 'char' in in_type:
            return None
    if need_exclude: return None

    duplicate = {}
    generated_examples = []

    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]
        # for k in range(1, K+1):
        for k in get_ks(bound, is_mult=True):
            e_ins_k = []
            for i,e_in in enumerate(e_ins):
                e_in_k = e_in
                if 'bit' not in input_types[i] and input_types[i] != 'int_N':
                    e_in_k = k_uniform_mult(e_in, k)
                e_ins_k.append(e_in_k)
            e_outs_k = []
            for i,e_out in enumerate(e_outs):
                e_out_k = e_out
                if 'bit' not in output_types[i] and output_types[i] != 'int_N':
                    e_out_k = k_uniform_mult(e_out, k)
                e_outs_k.append(e_out_k)
            e_ins_k_str = str(e_ins_k)
            e_outs_k_str = str(e_outs_k)
            if e_ins_k_str in original_examples_dict and original_examples_dict[e_ins_k_str] == e_outs_k_str:
                # same with some user-provided example, so skip
                continue
            if e_ins_k_str in duplicate:
                if e_outs_k_str not in duplicate[e_ins_k_str]:
                    if positive_prop:
                        return []
                else:
                    continue
            else:
                duplicate[e_ins_k_str] = []
            duplicate[e_ins_k_str].append(e_outs_k_str)
            generated_examples.append([e_ins_k, e_outs_k])
    return generated_examples


def generate_k_uniform_mult_invariant_examples(example_types, examples, bound=0, positive_prop=True):
    input_types, output_types = example_types
    need_exclude = False
    for in_type in input_types:
        # allow bit to remain unchanged in the generated examples
        # if 'bit' in in_type:
        #     return None
        # TODO: brute fix for char
        if 'char' in in_type:
            return None
    if need_exclude: return None

    duplicate = {}
    generated_examples = []

    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]
        # for k in range(1, K+1):
        for k in get_ks(bound, is_mult=True):
            e_ins_k = []
            for i,e_in in enumerate(e_ins):
                e_in_k = e_in
                if 'bit' not in input_types[i] and input_types[i] != 'int_N':
                    e_in_k = k_uniform_mult(e_in, k)
                e_ins_k.append(e_in_k)
            e_outs_k = []
            for i,e_out in enumerate(e_outs):
                e_out_k = e_out
                e_outs_k.append(e_out_k)
            e_ins_k_str = str(e_ins_k)
            e_outs_k_str = str(e_outs_k)
            if e_ins_k_str in original_examples_dict and original_examples_dict[e_ins_k_str] == e_outs_k_str:
                # same with some user-provided example, so skip
                continue
            if e_ins_k_str in duplicate:
                if e_outs_k_str not in duplicate[e_ins_k_str]:
                    if positive_prop:
                        return []
                else:
                    continue
            else:
                duplicate[e_ins_k_str] = []
            duplicate[e_ins_k_str].append(e_outs_k_str)
            generated_examples.append([e_ins_k, e_outs_k])
    return generated_examples


def k_rotate(arr, k):
    if not isinstance(arr, (list, tuple)):
        return arr
    res = arr[:]
    if k == 0: return res
    if k < 0: k = k % len(res)
    tmp = res[-k:]
    res[k:] = res[:-k]
    res[:k] = tmp
    return res

def all_rotations(arr):
    if not isinstance(arr, (list, tuple)):
        return arr
    duplicate = [str(arr)]
    arr_1 = arr[:]
    # include the original example in the soft constraints
    yield arr_1
    for _ in range(len(arr)):
        arr_1 = k_rotate(arr_1, 1)
        str_arr_1 = str(arr_1)
        if str_arr_1 in duplicate:
            return
        duplicate.append(str_arr_1)
        yield arr_1

def get_list_size(example_types, example, only_input=False):
    input_types, output_types = example_types
    list_size = -1
    for i, t_in in enumerate(input_types):
        if t_in == list or 'list' in t_in:
            if list_size == -1:
                list_size = len(example[0][i])
            else:
                if list_size != len(example[0][i]):
                    return 0
    if not only_input:
        output_has_no_list = True
        for i, t_out in enumerate(output_types):
            if t_out == list or 'list' in t_out:
                output_has_no_list = False
                if list_size == -1:
                    list_size = len(example[1][i])
                else:
                    if list_size != len(example[1][i]):
                        return 0
        if output_has_no_list: list_size = 0
    if list_size == -1: return 0
    else: return list_size

def get_matrix_shape(example_types, example):
    input_types, output_types = example_types
    # TODO: here assume eache matrix has same shape
    t_shape = None
    for i, t_in in enumerate(input_types):
        if 'matrix' in t_in:
            return example[0][i].shape
    for i, t_out in enumerate(output_types):
        if 'matrix' in t_out:
            return example[1][i].shape
    return (0, 0)

# deprecated, outdated
def generate_k_rotation_invariant_examples(example_types, examples, bound=0, positive_prop=True):
    duplicate = []
    generated_examples = []

    for example in examples:
        e_ins, e_out = example
        e_ins_str = str(e_ins)
        if e_ins_str in duplicate:
            continue
        list_size = get_list_size(example_types, example, only_input=True)
        if list_size == 0:
            # none of the input/output contains a list
            # no need to rotate
            generated_examples.append([e_ins, e_out])
        for _ in range(list_size):
            e_ins_r = []
            for i in range(len(e_ins)):
                e_ins[i] = k_rotate(e_ins[i], 1)
                e_ins_r.append(e_ins[i])
            e_ins_r_str = str(e_ins_r)
            if e_ins_r_str in duplicate:
                break
            duplicate.append(e_ins_r_str)
            generated_examples.append([e_ins_r, e_out])
    return generated_examples


def generate_k_rotation_neg_k_examples(example_types, examples, bound=0, positive_prop=True):
    duplicate = {}
    generated_examples = []

    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for example in examples:
        e_ins, e_outs = example
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]
        list_size = get_list_size(example_types, example)
        if list_size == 0:
            # none of the input/output contains a list
            # no need to rotate
            return None
            # generated_examples.append([e_ins, e_outs])
        for k in range(list_size):
            e_ins_r = []
            for e_in in e_ins:
                e_ins_r.append(k_rotate(e_in, k))
            e_outs_r = []
            for e_out in e_outs:
                e_outs_r.append(k_rotate(e_out, -k))
            e_ins_r_str = str(e_ins_r)
            e_outs_r_str = str(e_outs_r)
            if e_ins_r_str in original_examples_dict and original_examples_dict[e_ins_r_str] == e_outs_r_str:
                # same with some user-provided example, so skip
                continue
            if e_ins_r_str in duplicate:
                if e_outs_r_str not in duplicate[e_ins_r_str]:
                    if positive_prop:
                        return []
                else:
                    continue
            else:
                duplicate[e_ins_r_str] = []
            duplicate[e_ins_r_str].append(e_outs_r_str)
            generated_examples.append([e_ins_r, e_outs_r])
    return generated_examples
#     duplicate = []
#     generated_examples = []
# 
#     for e_in, e_out in examples:
#         e_in_str = str(e_in)
#         if e_in_str in duplicate:
#             continue
#         for e_in_r in all_rotations(e_in):
#             e_in_r_str = str(e_in_r)
#             if e_in_r_str in duplicate:
#                 break
#             duplicate.append(e_in_r_str)
#             # Check whether it's rotation or itself
#             if e_in_str != e_in_r_str:
#                 e_out = k_rotate(e_out, -1)
#             generated_examples.append([e_in_r, e_out])
#     return generated_examples


def str_matrix(mat):
    mat = [','.join([str(x) for x in row]) for row in mat]
    return '{%s}' % ','.join(mat)

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
    return ','.join(res)

def str_outputs(output_types, outputs):
    return str_inputs(output_types, outputs)


def str_inputs_sygus(input_types, inputs):
    res = []
    for i,e_in in enumerate(inputs):
        if input_types[i] == 'int' or input_types[i] == 'bit' or input_types[i] == int:
            res.append(str(e_in))
        elif input_types[i] == list or 'list' in input_types[i]:
            if isinstance(e_in[0], (list, tuple)):
                res.append(
                    '%s' % ' '.join([' '.join([str(x) for x in t]) for t in e_in])
                )
            else:
                if 'char' in input_types[i]:
                    res.append("{'%s'}" % "','".join(e_in))
                else:
                    res.append(
                        '%s' % ' '.join([str(x) for x in e_in])
                    )
        elif 'matrix' in input_types[i]:
            res.append(str_matrix(e_in))
        else:
            # TODO: brute fix for int_N
            res.append(str(e_in))
    return ' '.join(res)


def str_outputs_sygus(output_types, outputs):
    return str_inputs_sygus(output_types, outputs)


def generate_row_permutation_col_permutation_examples(example_types, examples, bound=0, positive_prop=True):
    if bound > 1000: bound = DEFAULT_BOUND_OF_TIME
    input_types, output_types = example_types

    duplicate = {}
    generated_examples = []

    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    bound_seconds = 0
    if bound < 0:
        bound_seconds = -bound

    for example in examples:
        e_ins, e_outs = example
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str,]

        matrix_shape = get_matrix_shape(example_types, example)
        if matrix_shape != (0,0):
            num_of_rows, num_of_cols = matrix_shape
            if bound <= 0:
                num_of_gened_examples = 0
                start_time = get_time()
                print('bound time', bound_seconds)
                for indices in itertools.permutations(range(num_of_rows)):
                    if bound_seconds:
                        stop_time = get_time()
                        if stop_time-start_time > bound_seconds:
                            print('Running out of time %s' % bound_seconds)
                            print('Got %s perturbed examples' % num_of_gened_examples)
                            break
                    if num_of_gened_examples == BOUND_OF_NUM_OF_EACH_EXAMPLE:
                        print('Enough number for this example %s' % BOUND_OF_NUM_OF_EACH_EXAMPLE)
                        break
                    e_ins_p = []
                    for i, e_in in enumerate(e_ins):
                        if 'matrix' in input_types[i]:
                            e_in_p = e_in[list(indices), :]
                        else:
                            e_in_p = e_in
                        e_ins_p.append(e_in_p)
                    e_outs_p = []
                    for i, e_out in enumerate(e_outs):
                        if 'matrix' in output_types[i]:
                            e_out_p = e_out[:, list(indices)]
                        else:
                            e_out_p = e_out
                        e_outs_p.append(e_out_p)
                    e_ins_p_str = str(e_ins_p)
                    e_outs_p_str = str(e_outs_p)
                    if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                        # same with some user-provided example, so skip
                        continue
                    if e_ins_p_str in duplicate:
                        if e_outs_p_str not in duplicate[e_ins_p_str]:
                            if positive_prop:
                                return []
                        else:
                            continue
                    else:
                        duplicate[e_ins_p_str] = []
                    duplicate[e_ins_p_str].append(e_outs_p_str)
                    num_of_gened_examples += 1
                    generated_examples.append([e_ins_p, e_outs_p])
            else:
                real_bound = get_bound(bound, e_ins, input_types, maxtrix_by_row=True)
                print('get real bound:', real_bound)
                l_bound = real_bound + EXTRA_SAMPLING_TIMES
                indices = list(range(num_of_cols))
                tmp_gen_exam = []
                while len(tmp_gen_exam) < real_bound and l_bound > 0:
                    l_bound -= 1
                    random.shuffle(indices)
                    e_ins_p = []
                    for i, e_in in enumerate(e_ins):
                        if 'matrix' in input_types[i]:
                            e_in_p = e_in[list(indices), :]
                        else:
                            e_in_p = e_in
                        e_ins_p.append(e_in_p)
                    e_outs_p = []
                    for i, e_out in enumerate(e_outs):
                        if 'matrix' in output_types[i]:
                            e_out_p = e_out[:, list(indices)]
                        else:
                            e_out_p = e_out
                        e_outs_p.append(e_out_p)
                    e_ins_p_str = str(e_ins_p)
                    e_outs_p_str = str(e_outs_p)
                    if e_ins_p_str in original_examples_dict and original_examples_dict[e_ins_p_str] == e_outs_p_str:
                        # same with some user-provided example, so skip
                        continue
                    if e_ins_p_str in duplicate:
                        if e_outs_p_str not in duplicate[e_ins_p_str]:
                            if positive_prop:
                                return []
                        else:
                            continue
                    else:
                        duplicate[e_ins_p_str] = []
                    duplicate[e_ins_p_str].append(e_outs_p_str)
                    tmp_gen_exam.append([e_ins_p, e_outs_p])
                generated_examples.extend(tmp_gen_exam)
        else:
            # none of the input/output contains a matrix
            return None
    return generated_examples


def generate_flip_up2n_bits_invariant_examples(example_types, examples, bound=0, positive_prop=True):

    def flip_helper(e_ins, cnt):
        t_e_ins_f = e_ins[:]
        if cnt == len(e_ins)-1:
            yield t_e_ins_f[:]
            t_e_ins_f[-1] = 1 - t_e_ins_f[-1]
            yield t_e_ins_f[:]
        else:
            for g in flip_helper(t_e_ins_f, cnt+1):
                yield g
            t_e_ins_f[cnt] = 1 - t_e_ins_f[cnt]
            for g in flip_helper(t_e_ins_f, cnt+1):
                yield g

    input_types, output_types = example_types
    all_types = input_types[:]
    all_types.extend(output_types)
    need_exclude = not functools.reduce(lambda x,y: x and y, map(lambda x: x=='bit', all_types))

    if need_exclude:
        return None

    duplicate = {}
    generated_examples = []
    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]

        e_outs_f = e_outs
        e_outs_f_str = str(e_outs_f)
        for e_ins_f in flip_helper(e_ins, 0):
            e_ins_f_str = str(e_ins_f)
            if e_ins_f_str in original_examples_dict and original_examples_dict[e_ins_f_str] == e_outs_f_str:
                continue
            if e_ins_f_str in duplicate:
                if e_outs_f_str not in duplicate[e_ins_f_str]:
                    if positive_prop:
                        return []
                else:
                    continue
            else:
                duplicate[e_ins_f_str] = []
            duplicate[e_ins_f_str].append(e_outs_f_str)
            generated_examples.append([e_ins_f, e_outs_f])
    return generated_examples


def generate_flip_all_input_bits_invariant_examples(example_types, examples, bound=0, positive_prop=True):
    input_types, output_types = example_types
    all_types = input_types[:]
    need_exclude = not functools.reduce(lambda x,y: x or y, map(lambda x: 'bit' in x, all_types))

    if need_exclude:
        return None

    duplicate = {}
    generated_examples = []
    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]

        e_ins_f = []
        for i, e_in in enumerate(e_ins):
            if 'list' in input_types[i]:
                e_ins_f.append([1-x for x in e_ins[0]])
            elif 'bit' == input_types[i]:
                e_ins_f.append(1-e_in)
        e_outs_f = e_outs
        e_ins_f_str = str(e_ins_f)
        e_outs_f_str = str(e_outs_f)
        if e_ins_f_str in original_examples_dict and original_examples_dict[e_ins_f_str] == e_outs_f_str:
            continue
        if e_ins_f_str in duplicate:
            if e_outs_f_str not in duplicate[e_ins_f_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_f_str] = []
        duplicate[e_ins_f_str].append(e_outs_f_str)
        generated_examples.append([e_ins_f, e_outs_f])
    return generated_examples


def generate_flip_one_input_bit_invariant_examples(example_types, examples, bound=0, positive_prop=True):
    def flip_helper(e_ins):
        for i in range(len(e_ins)):
            t_e_ins_f = e_ins[:]
            t_e_ins_f[i] = 1-t_e_ins_f[i]
            yield [t_e_ins_f]

    input_types, output_types = example_types
    all_types = input_types[:]
    need_exclude = not functools.reduce(lambda x,y: x or y, map(lambda x: 'bit' in x, all_types))

    if need_exclude:
        return None

    duplicate = {}
    generated_examples = []
    original_examples_dict = {}
    for e_ins, e_out in examples:
        original_examples_dict[str(e_ins)] = str(e_out)

    for e_ins, e_outs in examples:
        e_ins_str = str(e_ins)
        e_outs_str = str(e_outs)
        if e_ins_str in duplicate:
            if e_outs_str not in duplicate[e_ins_str]:
                if positive_prop:
                    return []
            else:
                continue
        else:
            duplicate[e_ins_str] = [e_outs_str]

        e_outs_f = e_outs
        e_outs_f_str = str(e_outs_f)
        for e_ins_f in flip_helper(e_ins[0]):
            e_ins_f_str = str(e_ins_f)
            if e_ins_f_str in original_examples_dict and original_examples_dict[e_ins_f_str] == e_outs_f_str:
                continue
            if e_ins_f_str in duplicate:
                if e_outs_f_str not in duplicate[e_ins_f_str]:
                    if positive_prop:
                        return []
                else:
                    continue
            else:
                duplicate[e_ins_f_str] = []
            duplicate[e_ins_f_str].append(e_outs_f_str)
            generated_examples.append([e_ins_f, e_outs_f])
    return generated_examples


PROPERTY_GENERATOR = {
    'permutation_invariant':           generate_permutation_invariant_examples,
    'permutation_permutation':         generate_permutation_permutation_examples,
    'k_uniform_add_k':                 generate_k_uniform_add_k_examples,
    'k_uniform_add_invariant':         generate_k_uniform_add_invariant_examples, # used for sygus
    #'k1_k2_uniform_add_k1_k2',
    'k_uniform_mult_k':                generate_k_uniform_mult_k_examples,
    'k_uniform_mult_invariant':        generate_k_uniform_mult_invariant_examples, # used for sygus
    #'k_rotation_invariant',
    'k_rotation_neg_k':                generate_k_rotation_neg_k_examples,
    'row_permutation_col_permutation': generate_row_permutation_col_permutation_examples,
    # 'flip_up2n_bits_invariant':        generate_flip_up2n_bits_invariant_examples,
    # 'flip_all_input_bits_invariant':   generate_flip_all_input_bits_invariant_examples,
    # 'flip_one_input_bit_invariant':    generate_flip_one_input_bit_invariant_examples,
}

properties = sorted(PROPERTY_GENERATOR.keys())
# Put negative properties before positive ones to let incr algo prefer negative ones if they are satisfied.
POSITIVE_PROPERTIES = properties
PROPERTIES = ['not_'+p for p in POSITIVE_PROPERTIES] + POSITIVE_PROPERTIES


def get_soft_constraints_code_helper(property_name, function_name, example_types, examples, bound=0, y_percent=-1, need_generation=True):
    negation = False
    org_property_name = property_name

    if property_name.startswith('not_'):
        if y_percent > 0 and y_percent <= 1:
            code = get_hard_constraints_code_helper(property_name, function_name, example_types, examples, bound=bound, neg_as_disjunction=False, y_percent=y_percent, need_generation=need_generation)
            return code

        negation = True
        property_name = property_name[4:]

    if property_name in PROPERTIES:
        generate_examples = PROPERTY_GENERATOR[property_name]
    else:
        print('generate_examples function for property %s is undefined' % property_name)
        return '', []
    if need_generation and generate_examples is not None:
        examples = generate_examples(example_types, examples, bound=bound, positive_prop=(not negation))
    if not examples: return '', []
    cost_variable = 'cost_' + org_property_name
    code = ''
    if negation:
        code = '    int %s = %d;\n' % (cost_variable, len(examples))
        for example in examples:
            code += '    if (%s(%s) != %s) %s -= 1;\n' % (
                function_name,
                str_inputs(example_types[0], example[0]),
                str_outputs(example_types[1], example[1]),
                cost_variable,
            )
    else:
        code = '    int %s = 0;\n' % cost_variable
        for example in examples:
            code += '    if (%s(%s) != %s) %s = 1;\n' % (
                function_name,
                str_inputs(example_types[0], example[0]),
                str_outputs(example_types[1], example[1]),
                cost_variable,
            )
    if not code:
        return '', []
    code += '    minimize(%s);\n' % cost_variable
    return 'harness void soft_constraints_%s() {\n%s}\n' % (org_property_name, code), examples

def get_hard_constraints_code_helper(property_name, function_name, example_types, examples, bound=0, neg_as_disjunction=True, y_percent=0.5, to_check_raw_sketch_output=False, need_generation=True):
    negation = False
    org_property_name = property_name
    if property_name.startswith('not_'):
        negation = True
        property_name = property_name[4:]

    if property_name == 'original':
        generate_examples = None
    elif property_name in PROPERTIES:
        generate_examples = PROPERTY_GENERATOR[property_name]
    else:
        print('generate_examples function for property %s is undefined' % property_name)
        return '', []
    if need_generation and generate_examples is not None:
        examples = generate_examples(example_types, examples, bound=bound, positive_prop=(not negation))
    if not examples: return '', []

    code_to_check_raw_sketch_output = ''
    if to_check_raw_sketch_output:
        code_to_check_raw_sketch_output = '%s\n' % gen_code_to_check_raw_sketch_output(example_types, examples, function_name, negation)
        return 'harness void hard_constraints_%s() {\n%s}\n' % (org_property_name, code_to_check_raw_sketch_output), []

    code = ''
    if negation:
        if neg_as_disjunction:
        # disjunctions
            tmp = ' ||\n        '.join(['(%s(%s) != %s)' % (
                            function_name,
                            str_inputs(example_types[0], example[0]),
                            str_outputs(example_types[1], example[1]),
                            ) for example in examples])
            code = '    assert (\n        %s\n    );\n' % tmp
        else:
            # at least y% of the neg examples are satisfied
            tmp_threshold = math.ceil(y_percent*len(examples))
            tmp_cnt_var = 'cnt_' + org_property_name
            code = '    int %s = 0;\n' % tmp_cnt_var
            for example in examples:
                code += '    if (%s(%s) != %s) %s += 1;\n' % (
                    function_name,
                    str_inputs(example_types[0], example[0]),
                    str_outputs(example_types[1], example[1]),
                    tmp_cnt_var,
                )
            code += '    assert (%s >= %d);\n' % (tmp_cnt_var, tmp_threshold)
    else:
        for example in examples:
            code += '    assert (%s(%s) == %s);\n' % (
                function_name,
                str_inputs(example_types[0], example[0]),
                str_outputs(example_types[1], example[1]),
            )

    return 'harness void hard_constraints_%s() {\n%s}\n' % (org_property_name, code), examples


def get_hard_constraints_code_helper_sygus(property_name, function_name, example_types, examples, bound=0, neg_as_disjunction=True, y_percent=0.5, to_check_raw_sketch_output=False, need_generation=True):
    negation = False
    org_property_name = property_name
    if property_name.startswith('not_'):
        negation = True
        property_name = property_name[4:]

    if property_name == 'original':
        generate_examples = None
    elif property_name in PROPERTIES:
        generate_examples = PROPERTY_GENERATOR[property_name]
    else:
        print('generate_examples function for property %s is undefined', property_name)
        return '', []
    if need_generation and generate_examples is not None:
        examples = generate_examples(example_types, examples, bound=bound, positive_prop=(not negation))
    if not examples: return '', []

    code_to_check_raw_sketch_output = ''
    if to_check_raw_sketch_output:
        code_to_check_raw_sketch_output = '%s\n' % gen_code_to_check_raw_sketch_output(example_types, examples, function_name, negation)
        return 'harness void hard_constraints_%s() {\n%s}\n' % (org_property_name, code_to_check_raw_sketch_output), []

    code = ''
    if negation:
        if neg_as_disjunction:
        # disjunctions
            tmp = ' ||\n        '.join(['(%s(%s) != %s)' % (
                            function_name,
                            str_inputs(example_types[0], example[0]),
                            str_outputs(example_types[1], example[1]),
                            ) for example in examples])
            code = '    assert (\n        %s\n    );\n' % tmp
        else:
            # at least y% of the neg examples are satisfied
            tmp_threshold = math.ceil(y_percent*len(examples))
            tmp_cnt_var = 'cnt_' + org_property_name
            code = '    int %s = 0;\n' % tmp_cnt_var
            for example in examples:
                code += '    if (%s(%s) != %s) %s += 1;\n' % (
                    function_name,
                    str_inputs(example_types[0], example[0]),
                    str_outputs(example_types[1], example[1]),
                    tmp_cnt_var,
                )
            code += '    assert (%s >= %d);\n' % (tmp_cnt_var, tmp_threshold)
    else:
        for example in examples:
            code += '(constraint (= (%s %s) %s));\n' % (
                function_name,
                str_inputs_sygus(example_types[0], example[0]),
                str_outputs_sygus(example_types[1], example[1]),
            )

    return ';perturbed by %s\n%s\n' % (org_property_name, code), examples


def gen_code_to_check_raw_sketch_output(example_types, examples, function_name, negation):
    # TODO: currently, only support disjunction strategy for negative properties
    code = ''
    output_vars = []
    var_index = -1
    output_type = example_types[1][0]
    for example in examples:
        var_index += 1
        # TODO: need to deal with int_N type
        if output_type == 'int' or output_type == 'bit':
            output_var = 'out_%d' % var_index
            code += '    %s %s = 0;\n' % (output_type, output_var)
            code += '    %s(%s, %s);\n' % (function_name, str_inputs(example_types[0], example[0]), output_var)
            output_vars.append(output_var)
        elif 'list' in output_type:
            t_type, _, t_size = output_type.split('_')
            output_var = 'out_%d' % var_index
            code += '    %s[%s] %s = 0;\n' % (t_type, t_size, output_var)
            code += '    %s(%s, %s);\n' % (function_name, str_inputs(example_types[0], example[0]), output_var)
            output_vars.append(output_var)

    if negation:
        tmp = ' ||\n        '.join(['(%s != %s)' % (
                        output_vars[index],
                        str_outputs(example_types[1], example[1]),
                        ) for index,example in enumerate(examples)])
        code += '    assert (%s);\n' % tmp
    else:
        for index, example in enumerate(examples):
            code += '    assert (%s == %s);\n' % (output_vars[index], str_outputs(example_types[1], example[1]))

    return code


def rank_property_sets(property_sets):

    bit_order = [
        'k_rotation_neg_k, not_permutation_invariant, not_permutation_permutation',
        'not_k_rotation_neg_k, not_permutation_permutation, permutation_invariant',
        'not_k_rotation_neg_k, not_permutation_invariant, permutation_permutation',
        'not_k_rotation_neg_k, not_permutation_invariant, not_permutation_permutation',
        'not_permutation_invariant, permutation_permutation',
        'not_permutation_invariant',
        'permutation_invariant',
    ]

    bit_no_neg_order = ['k_rotation_neg_k',]

    int_order = [
        'not_k_uniform_add_k, not_k_uniform_mult_k, not_permutation_invariant',
        'not_k_uniform_add_k, not_k_uniform_mult_k',
    ]

    mix_order = [
        'not_k_rotation_neg_k, not_k_uniform_mult_k, not_permutation_invariant, not_permutation_permutation',
        'not_k_rotation_neg_k, not_k_uniform_mult_k, not_permutation_permutation',
        'not_k_rotation_neg_k, not_k_uniform_add_k, not_k_uniform_mult_k, not_permutation_invariant, not_permutation_permutation',
        'not_k_uniform_add_k, not_k_uniform_mult_k',
        'k_uniform_add_k, not_k_uniform_mult_k',
        'not_k_rotation_neg_k, not_permutation_invariant',
        'not_k_rotation_neg_k',
    ]

    predefined_order = [
        'not_permutation_invariant',
        'permutation_invariant',
        'k_rotation_neg_k, not_permutation_invariant, not_permutation_permutation',
        'not_k_rotation_neg_k, not_permutation_permutation, permutation_invariant',
        'not_k_rotation_neg_k, not_permutation_invariant, not_permutation_permutation',
        'not_k_rotation_neg_k, not_permutation_invariant, permutation_permutation',
        'not_k_rotation_neg_k, permutation_invariant, permutation_permutation',

        'not_k_uniform_add_k, not_k_uniform_mult_k, not_permutation_invariant',
        'not_k_uniform_add_k, not_k_uniform_mult_k, permutation_invariant',
        'k_uniform_mult_k, not_k_uniform_add_k, permutation_invariant',
        'k_uniform_mult_k, permutation_invariant',
        'not_k_uniform_add_k, permutation_invariant',
        'not_k_uniform_add_k, not_k_uniform_mult_k',
        'k_uniform_mult_k, not_k_uniform_add_k',
        'k_uniform_add_k, not_k_uniform_mult_k',
    ]

    default_rank = 1024
    min_rank = default_rank + 100
    return_props = None
    for props in property_sets:
        props_str = ', '.join(sorted(props))
        try:
            tmp_rank = predefined_order.index(props_str)
        except ValueError:
            tmp_rank = default_rank
        print(props_str, tmp_rank)
        if tmp_rank < min_rank:
            min_rank = tmp_rank
            return_props = props

    return return_props


