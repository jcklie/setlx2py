#------------------------------------------------------------------------------
# setlx2py: test_codegen.py
#
# Unit tests for the Codegen class in setlx_codegen.py
# These are very shallow and cover only a small area
# Acceptance tests for code generation is seperate
#
# Copyright (C) 2014, Jan-Christoph Klie
# License: Apache v2
#------------------------------------------------------------------------------

from string import Template

from nose.tools import nottest, eq_

from setlx2py.builtin.setlx_set import SetlxSet

from setlx2py.setlx_util import run

import itertools
    
# Custom Asserts
# ==============    

def assert_res(source, variables={}, verbose=False, print_ast=False):
    ns = {}
    run(source, ns, verbose, print_ast)
    for key, value in variables.items():
        eq_(ns.get(key, None), value)

def assert_res_cases(s, cases, verbose=False, print_ast=False):
    header =  cases.pop(0)
    names, rname = header[:-1], header[-1]
    for case in cases:
        params, result = case[0:-1], case[-1]
        d = { k : v for k, v in zip(header, params) }
        source = s.substitute(d)
        assert_res(source, {rname : result}, verbose=verbose, print_ast=print_ast)        
                
# Tests
# ======

def test_identifier():
    ns = {'a' : 42}
    run('a;', ns)

def test_constant_int():
    run('42;')

def test_constant_str():
    assert_res('x := "foo";', {'x' : "foo"})

def test_constant_literal():
    assert_res("x := 'foo';", {'x' : "foo"})
    

# Assignment
# ----------

def test_assignment_simple():
    assert_res('x := 1;', {'x' : 1})

def test_assignment_augmented():
    assert_res('x := 1; x += 2;', {'x' : 3})
    assert_res('x := 3; x -= 2;', {'x' : 1})
    assert_res('x := 1; x *= 2;', {'x' : 2})
    assert_res('x := 6; x /= 2;', {'x' : 3})
    assert_res('x := 5; x %= 2;', {'x' : 1})

def test_assignment_augmented_set():
    s = Template("""
    s1 := { 1, 2 };
    s2 := { 2, 3 };
    s1 $op s2;
    """)
    
    cases = {
        '+='  : SetlxSet((1, 2, 3)), 
        '-='  : SetlxSet((1,)),
        '*='  : SetlxSet((2,)),
        '%='  : SetlxSet((1, 3)),
    }

    for op, result in cases.items():
        source = s.substitute(op=op)
        assert_res(source, {'s1' : result})

def test_assignment_list_simultaneous():
    assert_res('[x,y] := [1,2];', {'x' : 1, 'y' : 2})
    assert_res('[x,y] := [1,2]; [y,x] := [x,y];', {'x' : 2, 'y' : 1})

def test_assignment_underscore():
    assert_res('[x, _, z] := [1, 2, 3];', {'x' : 1, 'z' : 3})    

# Collections
# -----------

# Syntax sugar for creating collections

def test_set():
    assert_res('x := {};', {'x' : SetlxSet([])})
    assert_res('x := {1};', {'x' : SetlxSet([1])})
    assert_res('x := {1,2};', {'x' : SetlxSet([1,2])})
    assert_res('x := {1,2,3};', {'x' : SetlxSet([1,2,3])})
    assert_res('x := {1+3,2-4,3**0};', {'x' : SetlxSet([4,-2,1])})    

def test_list():
    assert_res('x := [];', {'x' :[]})
    assert_res('x := [1];', {'x' : [1]})
    assert_res('x := [1,2];', {'x' : [1,2]})
    assert_res('x := [1,2,3];', {'x' : [1,2,3]})
    assert_res('x := [1+3,2-4,3**0];', {'x' : [4,-2,1]})

# Range
# ~~~~~~

def test_range_set():
    assert_res('x := {1..5};', {'x' : SetlxSet([1,2,3,4,5]) })
    assert_res('x := {1..-1};', {'x' : SetlxSet([]) })
    assert_res('x := {1,3..10};', {'x' : SetlxSet([1,3,5,7,9]) })
    assert_res('x := {10,8..1};', {'x' : SetlxSet([10,8,6,4,2]) })
    assert_res('x := {-1,-2..-2};', {'x' : SetlxSet([-2, -1])})

def test_range_list():
    assert_res('x := [1..16];', {'x' : list(range(1,16+1)) })
    assert_res('x := [1..-1];', {'x' : list([]) })
    assert_res('x := [1,3..10];', {'x' : [1,3,5,7,9] })
    assert_res('x := [10,8..1];', {'x' : [10,8,6,4,2] })

# Comprehension
# ~~~~~~~~~~~~~

def test_set_comprehension_minimal():
    s = 'x := {2*n : n in [1..5]};'
    assert_res(s, {'x' : SetlxSet([2,4,6,8,10]) })

def test_set_comprehension_two_iterators():
    s = 'x := {a ** b: a in {1..3}, b in {2..4}};'
    assert_res(s, {'x' : SetlxSet([1, 4, 8, 9, 16, 27, 81]) })

def test_set_comprehension_cond():
    s = """
    p := 42;
    divisors := { t:t in {2..p-1} | p % t == 0 };
    """
    assert_res(s, {'divisors' : SetlxSet([2, 3, 6, 7, 14, 21])})    

def test_set_comprehension_cray():
    s = 'primes := { p:p in {2..100} | { t:t in {2..p-1} | p % t == 0 } == {} };'
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23,
              29, 31, 37, 41, 43, 47, 53, 59,
              61, 67, 71, 73, 79, 83, 89, 97]
    assert_res(s, {'primes' : SetlxSet(primes)})

def test_list_comprehension_cray():
    s = 'primes := [ p:p in [2..100] | [ t:t in [2..p-1] | p % t == 0 ] == [] ];'
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23,
              29, 31, 37, 41, 43, 47, 53, 59,
              61, 67, 71, 73, 79, 83, 89, 97]
    assert_res(s, {'primes' : primes})
    
# Binop
# -----

def test_binop_simple():
    assert_res('x := 1;', {'x' : 1})

def test_binop_add_three():
    assert_res('x := 1 + 2 + 3;', {'x' : 6})
    
def test_binop_mult_before_add():
    assert_res('x := 4 + 3 * 2;', {'x' : 10})
    assert_res('x := (4 + 3) * 2;', {'x' : 14})

def test_binop_power():
    assert_res('x :=  2 * 3  ** 2;', {'x' : 18})
    assert_res('x := (2 * 3) ** 2;', {'x' : 36})

def test_binop_precedence():
    assert_res('x := 2 +3 * 4;'   , {'x' : 2 + ( 3 * 4)})
    assert_res('x := 10 - 4 - 2;' , {'x' : ( 10 - 4 ) - 2})
    assert_res('x := 12 / 3 + 3;' , {'x' : (12 / 3) + 3})
    assert_res('x := 2 ** 3 + 3;' , {'x' : (2 ** 3) + 3 })
    assert_res('x := 12 / 2 * 3;' , {'x' : (12 / 2) * 3})
    assert_res('x := 12 / 2 / 3;' , {'x' : (12 / 2) / 3})
    assert_res('x := 18 / 3 ** 2;', {'x' : 18 /( 3 **2 )})

def test_binop_comparison():
    assert_res('x := 1 > 2;', {'x' : False})
    assert_res('x := 1 < 2;', {'x' : True})
    assert_res('x := 1 >= 1;', {'x' : True})
    assert_res('x := 1 <= 1;', {'x' : True})
    assert_res('x := 1 == 2;', {'x' : False})
    assert_res('x := 1 != 2;', {'x' : True})

def test_binop_logic_basic():
    assert_res('x := true && false;', {'x' : False})
    assert_res('x := true || false;', {'x' : True})

def test_binop_logic_complex():
    assert_res('x := true => false;',    {'x' : False})
    assert_res('x := false <==> false;', {'x' : True})
    assert_res('x := true <!=> false;',  {'x' : True})

# Collection operations
# ~~~~~~~~~~~~~~~~~~~~~

def test_binop_comparison_set():
    assert_res('x := 2 in {1..42};', {'x' : True})

def test_binop_set():
    s = Template("""
    s1 := { 1, 2 };
    s2 := { 2, 3 };
    result := s1 $op s2;
    """)
    
    cases = [
        ('op', 'result'),
        ('+' , SetlxSet([1, 2, 3])), 
        ('-' , SetlxSet([1])),
        ('*' , SetlxSet([2])),
        ('><', SetlxSet([(1, 2), (1, 3), (2, 2), (2, 3)])),
        ('%' , SetlxSet([1, 3])),
    ]
    assert_res_cases(s, cases)

def test_set_powerset():
    s = """
    s1 := { 1, 2 };
    result := 2 ** s1;
    """
    assert_res(s, {'result' : SetlxSet([(), (1,), (1,2), (2,)])})

def test_set_cartesian():
    s = """
    s1 := { 1, 2 };
    result := s1 ** 2;
    """
    assert_res(s, {'result' : SetlxSet([(1,1), (1,2), (2,1), (2,2)])})

def binop_list():
    assert_res('x := [1..3] + [5..10];', {'x' : [1, 2, 3, 5, 6, 7, 8, 9, 10]})
    assert_res('x := [1..3] * 3;', {'x' : [1, 2, 3] * 3})

# Unary
# ~~~~~ 

def test_unary_simple():
    assert_res('x := 5!;', {'x' : 120})
    assert_res('x := -5;', {'x' : -5})
    assert_res('x := !true;', {'x' : False})

def test_unary_set():
    assert_res('x := # {5, 7, 13};', {'x' : 3})
    assert_res('x := +/ {1..6**2};', {'x' : 666})
    assert_res('x := */ {1..5};', {'x' : 120})

def test_unary_list():
    assert_res('x := # [5, 7, 13];', {'x' : 3})
    assert_res('x := +/ [1..6**2];', {'x' : 666})
    assert_res('x := */ [1..5];', {'x' : 120})

# Quantors
# --------

def test_forall_simple():
    s = 'result := forall (x in {1..10} | x ** 2 <= 2 ** x);'
    assert_res(s, {'result' : False})

def test_forall_two_iterators():
    s = 'result := forall (x in {1..10}, y in [20..30] | x < y);'
    assert_res(s, {'result' : True})

def test_exists_simple():
    s = 'result := exists (x in {1..10} | 2 ** x < x ** 2);'
    assert_res(s, {'result' : True})

@nottest    
def test_exists_two_iterators():
    s = 'result := exists ([x, y] in [[a,b] : a in {1..10}, b in {1..10}] | 3*x - 4*y == 5);'
    assert_res(s, {'result' : True})

# Subscription
# ------------

def test_subscription_minimal():
    s = """
    lst := [99, 88, 44];
    x := lst[2]; 
    """
    assert_res(s, {'x' : 88})

def test_subscription_chained():
    s = """
    lst := [[1,2], [4,5], [9,2]];
    x := lst[2][1]; 
    """
    assert_res(s, {'x' : 4})

# Slice
# -----

def test_slice_list():
    assert_res('l := [1..100]; x := l[5..10];', {'x' : [5,6,7,8,9,10]})
    assert_res('l := [1..10]; x := l[..4];', {'x' : [1,2,3,4]})
    assert_res('l := [1..10]; x := l[4..];', {'x' : [4,5,6,7,8,9,10]})

def test_slice_string():
    assert_res('s := "abcdef"; x := s[2..5];', {'x' : "bcde"})
    assert_res('s := "abcdef"; x := s[2..];', {'x' : "bcdef"})
    assert_res('s := "abcdef"; x := s[..5];', {'x' : "abcde"})

# String Interpolation
# --------------------

def test_string_interpolation():
    assert_res('x := 42; s := "x = $x$";', {'s' : "x = 42"})
    assert_res('n :=  6; s := "$n$! = $n!$";', {'s' : "6! = 720"})    

@nottest
def test_escapes():
    assert_res('s := "a single \$-symbol";', {'s' : "a single $-symbol"}, True)    
    
# Compund statements
# ==================

# Procedures
# ----------

@nottest    
def test_procedure_primes():
    s = Template("""
    primes := procedure(n) {
        s := { 2..n };
        return s - { p*q : [p, q] in s >< s };
    };
    result := primes($n);
    """)

    cases = {
        '2'   : [2],
        '10'  : [2,3,5,7],
        '50' : [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47],
    }
    for n, result in cases.items():
        source = s.substitute(n=n)
        assert_res(source, {'result' : SetlxSet(result)})

def test_procedure_max():
    s = Template("""
    max := procedure(a, b) {
        if(a > b) {
            return a;
        } else {
            return b;
        }
    };
    result := max($a,$b);
    """)
    cases = [
        ('a', 'b', 'result'),
        (42, 3, 42),
        (23, 1337, 1337),
        (7, 7, 7),
    ]
    assert_res_cases(s, cases)

def test_procedure_two():
    s = Template("""
    factors := procedure(p) {
        return {f : f in { 1 .. p } | p % f == 0 };
    };
    primes := procedure(n) {
        return {p : p in { 2 .. n } | factors(p) == { 1, p } };
    };
    result := primes($n);
    """)
    
    cases = [
        ('n', 'result'),
        ('2' , SetlxSet([2])),
        ('10', SetlxSet([2,3,5,7])),
        ('50', SetlxSet([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47])),
    ]
    assert_res_cases(s, cases)

# Cached Procedures
# -----------------

def test_cached_procedure_fibonacci():
    s = Template("""
    fibonacci := cachedProcedure(n) {
        if (n in [0,1]) {
            return n;
        }
        return fibonacci(n-1) + fibonacci(n-2);
    };
    result := fibonacci($n);
    """)
    cases = [
        ('n', 'result'),
        ('0', 0),
        ('1', 1),
        ('2', 1),
        ('3', 2),
        ('4', 3),
        ('50', 12586269025),
    ]
    assert_res_cases(s, cases)  
    

# Lambda
# ------

def test_lambda_one_argument():
    s = """
    map := procedure(l, f) {
    return [ f(x) : x in l ];
    };
    result := map([1 .. 10], x |-> x * x);
    """
    assert_res(s, {'result' : [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]})

# If-Else
# -------

# If-No-Else
# ~~~~~~~~~~

def test_if_no_else_minimal():
    assert_res('if(true) {}', {})
    
def test_if_no_else_single():
    s = """
    x := 42;
    if(x >= 5) { y := 3; }
    """
    assert_res(s, {'x' : 42, 'y' : 3})

def test_if_no_else_double():
    s = """
    x := 6;
    if(x >= 5 && x != 7) {
        y := "Foo";
        z := "Bar";
    }
    """
    assert_res(s, {'x' : 6, 'y' : "Foo", 'z' : "Bar"})
    
# If-Else

def test_if_else_minimal():
    assert_res('if(true) {} else {}', {})

def test_if_else_single():
    s = """
    i := 23; // Illuminati
    if(i % 2 == 0) {
        parity := "Even";
    } else {
        parity := "Odd";
    }
    """
    assert_res(s, {'parity' : "Odd"})

def test_if_four_else_if_else():
    s = Template("""
    grade := '$grade';
    if(grade == "A") {
        descr := "Excellent";
    } else if(grade == "B") {
        descr := "Good";
    } else if(grade == "C") {
        descr := "Satisfactory";
    } else if(grade == "D") {
        descr := "Pass";
    } else if(grade == "F") {
        descr := "Fail";
    } else {
        descr := "Invalid input";
    }
    """)
    
    cases = [
        ('grade', 'descr'),
        ('A', 'Excellent'),
        ('B', 'Good'),
        ('C', 'Satisfactory'),
        ('D', 'Pass'),
        ('F', 'Fail'),
        ('J', 'Invalid input'),
    ]
    assert_res_cases(s, cases)

def test_if_nested_else_simple():
    s = Template("""
    if($num1 == $num2) {
        relation := "Equal";
    } else {
        if($num1 > $num2) { 
            relation := "Num1 greater";
        } else {
            relation := "Num2 greater";
        }
    }
    """)
    
    cases = [
        ('num1', 'num2', 'relation'),
        (1,1, "Equal"),
        (2,1, "Num1 greater"),
        (1,2, "Num2 greater"),
    ]
    assert_res_cases(s, cases)
        
def test_if_else_cray():
    s = Template("""
    sort3 := procedure(l) {
        [ x, y, z ] := l;
        if (x <= y) {
            if (y <= z) {
                 return [ x, y, z ];
            } else if (x <= z) {
                 return [ x, z, y ];
             } else {
                 return [ z, x, y ];
             }
         } else if (z <= y) {
             return [z, y, x];
         } else if (x <= z) {
             return [ y, x, z ];
         } else {
             return [ y, z, x ];
        }
    };
    result := sort3([$a, $b, $c]);
    """)
    cases = [
        ('a', 'b', 'c', 'result'),
    ]
    cases += [(a,b,c, sorted((a,b,c))) for a,b,c in itertools.permutations(range(1,4), 3)]
    assert_res_cases(s, cases)
                     
# Switch-Statement

def test_switch_even_odd():
    s = Template("""
    parity := procedure(n) {
        switch {
            case n % 2 == 0 : return 'Even';
            case n % 2 == 1 : return 'Odd';
        }
    };
    result := parity($n);
    """)
    cases = [
        ('n', 'result'),
        (42, 'Even'),
        (1337, 'Odd'),
    ]
    assert_res_cases(s, cases)

def test_switch_grades():
    s = Template("""
    gradez := procedure(grade) {
        switch {
            case grade == 'A' : return 'Excellent';
            case grade == 'B' : return 'Good';
            case grade == 'C' : return 'Satisfactory';
            case grade == 'D' : return 'Pass';
            case grade == 'F' : return 'Fail';
            default           : return 'Invalid input';
        }
    };
    descr := gradez('$grade');
    """)
    cases = [
        ('grade', 'descr'),
        ('A', 'Excellent'),
        ('B', 'Good'),
        ('C', 'Satisfactory'),
        ('D', 'Pass'),
        ('F', 'Fail'),
        ('J', 'Invalid input'),
    ]
    assert_res_cases(s, cases)

def test_switch_sort3():
    s = Template("""
    sort3 := procedure(l) {
        [ x, y, z ] := l;
        switch {
        case x <= y && y <= z: return [ x, y, z ];
        case x <= z && z <= y: return [ x, z, y ];
        case y <= x && x <= z: return [ y, x, z ];
        case y <= z && z <= x: return [ y, z, x ];
        case z <= x && x <= y: return [ z, x, y ];
        case z <= y && y <= x: return [ z, y, x ];
        default: print("Impossible error occurred!");
        }
    };
    result := sort3([$a, $b, $c]);
    """)
    cases = [
        ('a', 'b', 'c', 'result'),
    ]
    cases += [(a,b,c, sorted((a,b,c))) for a,b,c in itertools.permutations(range(1,4), 3)]
    assert_res_cases(s, cases)

# Match-Statement
# ---------------


def test_match_reverse():
    s = Template("""
    reverse := procedure(s) {
        match (s) {
            case []   : return s;
            case [c|r]: return reverse(r) + c;
            default   : abort("type error in reverse(s)");
        }
    };
    result := reverse('$s');
    """)
    cases = [
        ('s', 'result'),
        ('', ''),
        ('A', 'A'),
        ('ab', 'ba'),
        ('maoam', 'maoam'),
    ]
    assert_res_cases(s, cases)

def test_match_reverse_pairs():
    s = Template("""
    reversePairs := procedure(s) {
         match (s) {
             case []: return s;
             case [c]: return c;
             case [a, b | r]: return b + a + reversePairs(r);
         }
    };
    result := reversePairs('$s');
    """)
    
    cases = [
        ('s', 'result'),
        ('', ''),
        ('j', 'j'),
        ('xy', 'yx'),
        ('rentiere sind toll', 'ertneiers ni dotll'),
    ]
    assert_res_cases(s, cases)
    

    
# For-Loop
# --------

def test_for_loop_minimal():
    s = 'for(x in [1..10]) {}'
    assert_res(s)

def test_for_loop_single():
    s = """
    accum := 0;
    for(x in [1..10]) {
        accum += x;
    }
    """
    assert_res(s, {'accum' : 55})
    

def test_for_loop_double():
    s = """
    accum := {};
    for(x in {1..2}, y in {-1,-2..-2}) {
        accum += {[x, y]};
    }
    """
    assert_res(s, {'accum' : SetlxSet([[1, -2], [1, -1], [2, -2], [2, -1]])})
    
# While-Loop
# ----------

def test_while_collatz():
    s = Template(
    """
    f := procedure(n) {
        if (n == 0) {
            return 1;
        }
        while (n != 1) {
            if (n % 2 == 0) {
                n /= 2;
            } else {
                n := 3 * n + 1;
            }
        }
            return n;
    };
    result := f($n);     
    """)
    cases = [
        ('n', 'result'),
        (42, 1),
        (0, 1),
        (1, 1),
    ]
    assert_res_cases(s, cases)
    
# Loop flow control

def test_continue():
    s = """
    even := []; 
    for(n in [1..10]) { 
        if(n % 2 == 0) { even += [n]; } 
        else { continue; } 
    }                                                   
    """
    assert_res(s, {'even' : [2, 4, 6, 8, 10]})    
    
def test_break():
    s = """
    s := "";
    for(c in "foObar") {
        if(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ") {             
            break;
        } else {
            s += c;
        }
    }                                                   
    """
    assert_res(s, {'s' : 'fo'})    

@nottest
def test_break_and_continue():
    s = """
    lst := [];

    n := 0; 
    while (n < 10) { 
        n := n + 1; 
        
        if (n == 2) { continue; } 
        if (n == 4) { break; } 
        lst += [n];
    } 

    """
    assert_res(s, {'s' : [1, 3]})    