import os

from nose.tools import eq_, nottest

from setlx2py.setlx_util import run

FIXTURES = os.path.abspath('tests/fixtures')
SOURCE = os.path.join(FIXTURES, 'source')
REFERENCE = os.path.join(FIXTURES, 'reference')

def has_same_result(source_path, ref_path, verbose=False, print_ast=False):
    with open(source_path, 'r') as f_source, open(ref_path, 'r') as f_ref:
        source = f_source.read()
        reference = f_ref.read()

    result = run(source, verbose=verbose, print_ast=print_ast)
    if verbose or result != reference:
        print('')
        print(source_path)
        print(result)
        print(reference)     

    return result == reference

def assert_same_result(folder,verbose=False):
    all_correct = True
    wrong_files = []

    entries = [os.path.join(folder,f) for f in os.listdir(folder)]
    files = [f for f in entries if os.path.isfile(f)]
    
    for source_path in files:
        name = os.path.basename(source_path)
        ref_path = os.path.join(folder, 'reference', name + '.reference')
        current_same_result = has_same_result(source_path, ref_path, verbose)

        if not current_same_result:
            all_correct = False
            wrong_files.append(source_path)

    correct_count = len(files) - len(wrong_files)
    msg =  'Ran [{0}/{1}]\n'.format(correct_count, len(files))
    msg += 'The following files had different results: '
    msg += '\n{0}'.format('\n'.join(wrong_files))
    
    assert all_correct, msg

def test_source_results():
    assert_same_result(SOURCE)