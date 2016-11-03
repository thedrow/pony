from __future__ import absolute_import, print_function
from pony.py23compat import PY2, imap, basestring, unicode

import re, os.path, sys, inspect, types, warnings

from datetime import datetime
from itertools import count as _count
from inspect import isfunction
from time import strptime
from collections import defaultdict
from functools import update_wrapper
from xml.etree import cElementTree

import pony
from pony import options

from pony.thirdparty.compiler import ast
from pony.thirdparty.decorator import decorator as _decorator

if pony.MODE.startswith('GAE-'): localbase = object
else: from threading import local as localbase

expr1_re = re.compile(r'''
        ([A-Za-z_]\w*)  # identifier (group 1)
    |   ([(])           # open parenthesis (group 2)
    ''', re.VERBOSE)

expr2_re = re.compile(r'''
     \s*(?:
            (;)                 # semicolon (group 1)
        |   (\.\s*[A-Za-z_]\w*) # dot + identifier (group 2)
        |   ([([])              # open parenthesis or braces (group 3)
        )
    ''', re.VERBOSE)

expr3_re = re.compile(r"""
        [()[\]]                   # parenthesis or braces (group 1)
    |   '''(?:[^\\]|\\.)*?'''     # '''triple-quoted string'''
    |   \"""(?:[^\\]|\\.)*?\"""   # \"""triple-quoted string\"""
    |   '(?:[^'\\]|\\.)*?'        # 'string'
    |   "(?:[^"\\]|\\.)*?"        # "string"
    """, re.VERBOSE)

def parse_expr(s, pos=0):
    z = 0
    match = expr1_re.match(s, pos)
    if match is None: raise ValueError()
    start = pos
    i = match.lastindex
    if i == 1: pos = match.end()  # identifier
    elif i == 2: z = 2  # "("
    else: assert False  # pragma: no cover
    while True:
        match = expr2_re.match(s, pos)
        if match is None: return s[start:pos], z==1
        pos = match.end()
        i = match.lastindex
        if i == 1: return s[start:pos], False  # ";" - explicit end of expression
        elif i == 2: z = 2  # .identifier
        elif i == 3:  # "(" or "["
            pos = match.end()
            counter = 1
            open = match.group(i)
            if open == '(': close = ')'
            elif open == '[': close = ']'; z = 2
            else: assert False  # pragma: no cover
            while True:
                match = expr3_re.search(s, pos)
                if match is None: raise ValueError()
                pos = match.end()
                x = match.group()
                if x == open: counter += 1
                elif x == close:
                    counter -= 1
                    if not counter: z += 1; break
        else: assert False  # pragma: no cover
