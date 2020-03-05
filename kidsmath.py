#!/usr/bin/env python3


import argparse
import random
import math
import ast
import operator as op
import pprint


DEBUG = False


def main():
    parser = argparse.ArgumentParser(description='Generate kids math tests')
    parser.add_argument('--debug', '-d', dest='debug',
                        action='store_true', help='debug mode')
    args = parser.parse_args()
    global DEBUG
    if args.debug:
        DEBUG = True
    lower_limit = 1
    upper_limit = 10
    operators = ['+', '-', '*', '/']
    n_numbers = 6
    n_tests = 10

    tests, results = gen_test(operators,
                              upper_limit, lower_limit, n_numbers, n_tests)
    if DEBUG:
        for i, test in enumerate(tests):
            try:
                answer = eval_expr(test)
            except SyntaxError:
                answer = 'f'
            if answer == results[i]:
                f = 'correct'
            else:
                f = 'incorrect'
            print('%-50s%-10s' % ('%s = %s' % (test, results[i]), f))
    return None


def gen_test(operators, upper_limit, lower_limit, n_numbers, n_tests):
    func_of_operator = {
        '+': numbers_for_plus,
        '-': numbers_for_minus,
        '*': numbers_for_multiple,
        '/': numbers_for_divide,
    }
    all_tests = []
    all_results = []
    i = 0
    while i < n_tests:
        numbers, generated_operators, result = gen_random(
            operators, func_of_operator, upper_limit, lower_limit, n_numbers
        )
        all_tests.append(gen_formula(numbers, generated_operators))
        all_results.append(result)
        i += 1
    return all_tests, all_results


def gen_formula(numbers, operators):
    if len(operators) == 1:
        operator = ' %s ' % operators[0]
        return operator.join([str(i) for i in numbers])
    formula = ''
    max_n = len(operators) - 1
    n = max_n
    while n >= 0:
        if n == max_n:
            num_2nd = numbers[n + 1]
            parenthesis_1 = '('
            parenthesis_2 = ')'
        elif n == 0:
            num_2nd = formula
            parenthesis_1 = ''
            parenthesis_2 = ''
        else:
            num_2nd = formula
            parenthesis_1 = '('
            parenthesis_2 = ')'
        formula = '%s%s %s %s%s' % (
            parenthesis_1, numbers[n], operators[n], num_2nd, parenthesis_2
        )
        n -= 1
    return formula


def gen_random(
    operators, func_of_operator,
    upper_limit, lower_limit, n_numbers
):
    numbers = []
    generated_operators = []
    target = random.randint(lower_limit, upper_limit)
    i = 0
    remain = target
    while i < n_numbers - 1:
        operator = random.choice(operators)
        n, remain = func_of_operator[operator](remain,
                                               lower_limit, upper_limit)
        numbers.append(n)
        generated_operators.append(operator)
        i += 1
    numbers.append(remain)
    return numbers, generated_operators, target


def numbers_for_plus(target, lower_limit, upper_limit):
    if target:
        n1 = random.randint(1, target)
        if n1 == target:
            n1 -= 1
    else:
        n1 = 0
    n2 = target - n1
    return n1, n2


def numbers_for_minus(target, lower_limit, upper_limit):
    n1 = random.randint(target, upper_limit)
    if n1 == target:
        n1 += 1
    n2 = n1 - target
    return n1, n2


def numbers_for_multiple(target, lower_limit, upper_limit):
    n1 = int(random.choice(divisors(target)))
    n2 = int(target / n1)
    return n1, n2


def numbers_for_divide(target, lower_limit, upper_limit):
    multiple = int(upper_limit / target)
    rand = random.choice(range(1, multiple + 1))
    n1 = target * rand
    n2 = rand
    return n1, n2


def divisors(n):
    divs = [1]
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divs.extend([i, n/i])
    if n:
        divs.extend([n])
    return list(set(divs))


def eval_expr(expr):
    return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
    # supported operators
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
                 ast.USub: op.neg}

    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        return operators[type(node.op)](eval_(node.left), eval_(node.right))
    elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_(node.operand))
    else:
        raise TypeError(node)


if __name__ == '__main__':
    main()
