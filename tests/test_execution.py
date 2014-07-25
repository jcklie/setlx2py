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

def assert_same_result(folder, name, verbose=False, print_ast=False):
    random.seed(0)
    source_path = os.path.join(folder, name)
    name = os.path.basename(name)
    ref_path = os.path.join(folder, 'reference', name + '.reference')
    assert has_same_result(source_path, ref_path, verbose, print_ast), name


def test_example_results():
    files_to_test = [
         # 'aufgaben_zur_gdi.stlx', LIST ASSIGNMENT
        'ggt.stlx',
        'kgv.stlx',
        # 'klausur_aufgabe_power.stlx',
        'min-sort.stlx',
        
        'primes-sieve.stlx',
        'primes-tuple.stlx',
        'tautology.stlx'
    ]

    for stlx_file in files_to_test:
        assert_same_result(SOURCE_EXAMPLES, stlx_file) 

def test_logic_results():     

    # assert_same_result(SOURCE_LOGIC, 'davis-putnam.stlx') PARSE
    # assert_same_result(SOURCE_LOGIC, 'fibonacci-combinatorics.stlx') SCOPE
    # 'transitive-closure.stlx' LIST ASSIGNMENT
    
    files_to_test = [  
        'allValuations.stlx',
        'arb.stlx',
        'count.stlx',
        'evaluateOld.stlx',
        'fibonacci-combinatorics.stlx',
        'find-path.stlx',
        'fixpoint.stlx',
        'from.stlx',
        'function.stlx', 
        'ggt-fast.stlx',
        'ggt-loop.stlx',
#        'knfOld.stlx',
        'min-sort.stlx',
        'mySort.stlx',
        'path-cyclic.stlx',
        'primes-eratosthenes.stlx',
        'primes-for.stlx',
        'primes-forall.stlx',
        'primes-sieve.stlx',
        'primes-slim.stlx',
        'primes-tuple.stlx',
        'primes-while.stlx',        
        'simple.stlx',
        'simple-tuple.stlx',
        'solve.stlx',
        'sort.stlx',        
        'sum.stlx',
        'sum-recursive.stlx',
        'switch.stlx',       
    ]
    
    for stlx_file in files_to_test:
        assert_same_result(SOURCE_LOGIC, stlx_file) 
    
    
