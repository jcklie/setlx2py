setlx2py
========

This is a source-to-source compiler from setlX to Python 3. It was implemented during a one-year project for university.

The homepage for setlX can be found on <http://randoom.org/Software/SetlX>.

Dependencies
============

* Python 3.3.2
* PLY (Python Lex-Yacc)

Virtualenv
==========
virtualenv is a tool to create isolated Python environments. To create a fresh python installation, just enter the following commmand:

	cd "PATH_TO_README"
	virtualenv -p python3.3 python3.3
	source venv/bin/activate
	pip install -r REQUIREMENTS.txt	

Then, the prompt should have changed and start with 

	(venv)

Whenever a command related to this project is issued, the step with 

	source venv/bin/activate

has to be repeated, since only the then Python executable of this very project is used.
Shovel
=====

To create the Python AST representation for the parse tree, use

	shovel build.ast

[![Build Status](https://travis-ci.org/Rentier/setlx2py.png?branch=master)](https://travis-ci.org/Rentier/setlx2py)
