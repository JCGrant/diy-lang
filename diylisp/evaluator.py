# -*- coding: utf-8 -*-

from operator import add, sub, floordiv, mul, gt, mod

from .types import Environment, LispError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, is_integer, is_string
from .parser import unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports, 
making your work a bit easier. (We're supposed to get through this thing 
in a day, after all.)
"""

def evaluate_quote(ast, env):
    return ast[1]

def evaluate_atom(ast, env):
    return is_atom(evaluate(ast[1], env))

def evaluate_eq(ast, env):
    arg1 = evaluate(ast[1], env)
    arg2 = evaluate(ast[2], env)
    return is_atom(arg1) and is_atom(arg2) and arg1 == arg2

def evaluate_if(ast, env):
    condition = evaluate(ast[1], env)
    if condition:
        return evaluate(ast[2], env)
    else:
        return evaluate(ast[3], env)

def evaluate_define(ast, env):
    if len(ast) != 3:
        raise LispError('Wrong number of arguments in define')
    symbol = ast[1]
    if not is_symbol(symbol):
        raise LispError(str(symbol) + ' is a non-symbol')
    value = evaluate(ast[2], env)
    env.set(symbol, value)

def evaluate_lambda(ast, env):
    if len(ast) != 3:
        raise LispError('Wrong number of arguments in lambda')
    params = ast[1]
    if not is_list(params):
        raise LispError('Lambda params must be a list')
    body = ast[2]
    return Closure(env, params, body)

SPECIAL_FORMS = {
    'quote': evaluate_quote,
    'atom': evaluate_atom,
    'eq': evaluate_eq,
    'if': evaluate_if,
    'define': evaluate_define,
    'lambda': evaluate_lambda,
}

def evaluate_special_forms(ast, env):
    return SPECIAL_FORMS[ast[0]](ast, env)

MATHS_OPS = {
    '+': add,
    '-': sub,
    '/': floordiv,
    '*': mul,
    '>': gt,
    'mod': mod
}

def evaluate_maths(ast, env):
    op = ast[0]
    arg1 = evaluate(ast[1], env)
    arg2 = evaluate(ast[2], env)
    if not is_integer(arg1) or not is_integer(arg2):
        raise LispError('Math operands must be numeric')
    return MATHS_OPS[op](arg1, arg2)

def evaluate_closure(ast, env):
    closure = ast[0]
    args = [evaluate(arg, env) for arg in ast[1:]]
    params = closure.params
    if len(args) != len(params):
        raise LispError('Number of arguments does not much number of function parameters')
    inside_env = closure.env.extend(dict(zip(params, args)))
    return evaluate(closure.body, inside_env)

def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if is_boolean(ast) or is_integer(ast):
        return ast
    if is_list(ast):
        exp = ast[0]
        if exp in SPECIAL_FORMS.keys():
            return evaluate_special_forms(ast, env)
        if exp in MATHS_OPS.keys():
            return evaluate_maths(ast, env)
        if is_closure(exp):
            return evaluate_closure(ast, env)
    return env.lookup(ast)
