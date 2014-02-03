setlx2py
========

This is a source-to-source compiler from setlX to Python 3. It was implemented during a one-year project for university.

The homepage for setlX can be found on <http://randoom.org/Software/SetlX>.

Dependencies
============

* Python 2.7.3
* PLY (Python Lex-Yacc)
* ast-gen (only for development)

Play with it
============

## Parser

Load the parser and start an interactive shell with

    make parser

You can now use the *parser* variable to parse text:

    >>> parser.parse("a;")
    ('FileAST', ('Identifier', 'a'))

## AST

Rebuild the AST classes (needs ast-gen installed):

    make ast

## Run tests

The unit test suite can be run with

    make test

[![Build Status](https://travis-ci.org/Rentier/setlx2py.png?branch=master)](https://travis-ci.org/Rentier/setlx2py)