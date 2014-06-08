import os
import sys
import random

from StringIO import StringIO

from nose.tools import eq_, nottest

from setlx2py.setlx_util import run

FIXTURES = os.path.abspath('tests/fixtures')
REFERENCE = os.path.join(FIXTURES, 'reference')

SOURCE_EXAMPLES = os.path.join(FIXTURES, 'examples')
SOURCE_LOGIC = os.path.join(FIXTURES, 'logic')

def has_same_result(source_path, ref_path, verbose=False, print_ast=False):
    with open(source_path, 'r') as f_source, open(ref_path, 'r') as f_ref:
        source = f_source.read()
        reference = f_ref.read()

    # Pipe stdout to a variable

    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    try:
        run(source, verbose=verbose, print_ast=print_ast)
        result =  mystdout.getvalue()
    except Exception as e:
        raise e
    finally:
        sys.stdout = old_stdout

    if verbose or result != reference:
        print('')
        print(source_path)
        print(result)
        print(reference)     

    return result == reference

"""    
def assert_same_result(folder,verbose=False):
    all_correct = True
    wrong_files = []

    entries = [os.path.join(folder,f) for f in os.listdir(folder)]
    files = [f for f in entries if os.path.isfile(f)]

    for source_path in files:
        name = os.path.basename(source_path)
        ref_path = os.path.join(folder, 'reference', name + '.reference')
        current_same_result = has_same_result(source_path, ref_path, verbose, verbose)

        if not current_same_result:
            all_correct = False
            wrong_files.append(source_path)

    correct_count = len(files) - len(wrong_files)
    msg =  'Ran [{0}/{1}]\n'.format(correct_count, len(files))
    msg += 'The following files had different results: '
    msg += '\n{0}'.format('\n'.join(wrong_files))
    
    assert all_correct, msg
"""

def assert_same_result(folder, name, verbose=False, print_ast=False):
    random.seed(0)
    source_path = os.path.join(folder, name)
    name = os.path.basename(name)
    ref_path = os.path.join(folder, 'reference', name + '.reference')
    assert has_same_result(source_path, ref_path, verbose, print_ast), name

def test_example_results():
    assert_same_result(SOURCE_EXAMPLES, 'ggt.stlx')
    assert_same_result(SOURCE_EXAMPLES, 'min-sort.stlx')
    assert_same_result(SOURCE_EXAMPLES, 'kgv.stlx')
    assert_same_result(SOURCE_EXAMPLES, 'primes-sieve.stlx')
    assert_same_result(SOURCE_EXAMPLES, 'tautology.stlx')

def test_logic_results():    
    # assert_same_result(SOURCE_LOGIC, 'knf.stlx') TERMS/MATCHING
    # assert_same_result(SOURCE_LOGIC, 'davis-putnam.stlx') PARSE
    # assert_same_result(SOURCE_LOGIC, 'fibonacci-combinatorics.stlx') SCOPE
    # 'transitive-closure.stlx' LIST ASSIGNMENT
    
    files_to_test = [  
        'allValuations.stlx',
        'fixpoint.stlx',
        'primes-for.stlx',
        'primes-eratosthenes.stlx',
        'count.stlx',
        'from.stlx',
        'arb.stlx',
        'mySort.stlx',
        'min-sort.stlx',
        'ggt-loop.stlx',
        'evaluateOld.stlx',
        'ggt-fast.stlx',
        'switch.stlx',
        'sum-recursive.stlx',
        'sort.stlx',
        'sum.stlx',
        'primes-forall.stlx',
        'primes-sieve.stlx',
        'primes-slim.stlx',
        'primes-tuple.stlx',
        'simple.stlx',
        'solve.stlx',
        'path-cyclic.stlx',
        'primes-while.stlx',
        'simple-tuple.stlx',        
    ]
    
    for stlx_file in files_to_test:
        assert_same_result(SOURCE_LOGIC, stlx_file) 
    
    