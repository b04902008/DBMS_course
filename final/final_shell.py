import fcntl
import sys
import subprocess
import os
import time
import re

from subprocess import Popen, PIPE, DEVNULL

import numpy as np
import pymysql as sql

usingDB = ""

class Stack(object):
    def __init__(self, elements):
        if elements:
            self.stack = elements
        else:
            self.stack = []

    def __str__(self):
        return ', '.join(list(map(str, self.stack)))

    def push(self, element):
        self.stack.append(element)

    def peek(self):
        try:
            return self.stack[-1]
        except IndexError:
            return None

    def pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            return None

    def len(self):
        return len(self.stack)

    def copy(self):
        return self.stack[:]

def is_digit(num):
    try:
        float(num)
        return True
    except:
        return False

def printTable(string):
    tokens = string.split(',')
    tableList = [t.strip().split('.')[0] for t in tokens]
    columnList = [t.strip().split('.')[1] for t in tokens]
    tableMaxLen = max(np.max([len(t) for t in tableList]), len("TABLE_NAME"))
    columnMaxLen = max(np.max([len(c) for c in columnList]), len("COLUMN_NAME"))

    print("+-%s-+-%s-+" % ('-'*tableMaxLen, '-'*columnMaxLen))
    print("| %s%s | %s%s |" % ("TABLE_NAME", ' '*(tableMaxLen-len("TABLE_NAME")), "COLUMN_NAME", ' '*(columnMaxLen-len("COLUMN_NAME"))))
    print("+-%s-+-%s-+" % ('-'*tableMaxLen, '-'*columnMaxLen))
    for t, c in zip(tableList, columnList):
        print("| %s%s | %s%s |" % (t, ' '*(tableMaxLen-len(t)), c, ' '*(columnMaxLen-len(c))))
    print("+-%s-+-%s-+" % ('-'*tableMaxLen, '-'*columnMaxLen))

def infix_to_postfix(infix):
    priority = {'=': 0, '!=': 0, '>': 0, '<': 0, '>=': 0, '<=': 0, 'not': 1, 'and': 2, 'or': 3}
    stack = Stack(None)
    postfix = []

    for element in infix:
        if element in priority:
            while stack.len() > 0 and stack.peek() != '(' and priority[element] >= priority[stack.peek()]:
                postfix.append(stack.pop())
            stack.push(element)
        elif element == '(':
            stack.push(element)
        elif element == ')':
            while stack.peek() != '(':
                postfix.append(stack.pop())
            stack.pop()
        else:
            postfix.append(element)

    while stack.len() > 0:
        postfix.append(stack.pop())
    postfix.reverse()

    return postfix

def aggregate(stack, table, attr):
    aggregation = ['max', 'min', 'count', 'sum', 'avg', 'MAX', 'MIN', 'COUNT', 'SUM', 'AVG']
    operand = stack.pop()
    if not is_digit(operand):
        results = np.zeros(len(attr))
        if operand in aggregation:
            with sql.connect(host='localhost', user='root', password='root', db=usingDB) as conn:
                for i in range(len(attr)):
                    conn.execute("SELECT %s(%s) FROM %s" % (operand, attr[i], table))
                    result = conn.fetchall()
                    results[i] = result[0][0]
        elif operand.lower() == 'null':
            with sql.connect(host='localhost', user='root', password='root', db=usingDB) as conn:
                for i in range(len(attr)):
                    conn.execute("SELECT COUNT(*) FROM %s WHERE %s IS NULL" % (table, attr[i]))
                    result1 = conn.fetchall()
                    conn.execute("SELECT COUNT(*) FROM %s" % (table))
                    result2 = conn.fetchall()
                    results[i] = result1[0][0] / result2[0][0]
        elif operand.lower() == 'std':
            with sql.connect(host='localhost', user='root', password='root', db=usingDB) as conn:
                for i in range(len(attr)):
                    conn.execute("SELECT %s FROM %s WHERE %s IS NOT NULL" % (attr[i], table, attr[i]))
                    result = conn.fetchall()
                    result = np.array(result)[:, 0]
                    results[i] = np.std(result)
        elif operand[:4] == 'cor(' and operand[-1] == ')':
            results = correlate(table, attr, operand[4:-1])
        else:
            return None
        return results
    else:
        return float(operand)

def correlate(table1, attr1, attr2):
    dot = attr2.find('.')
    if dot == -1:
        table2 = table1
    else:
        table2 = attr2[:dot]
        attr2 = attr2[dot+1:]
    # print('table2', table2, 'attr2', attr2)
    results = np.zeros(len(attr1))
    with sql.connect(host='localhost', user='root', password='root', db=usingDB) as conn:
        if table1 == table2:
            for i in range(len(attr1)):
                conn.execute("SELECT %s, %s FROM %s WHERE %s IS NOT NULL AND %s IS NOT NULL" %
                            (attr1[i], attr2, table1, attr1[i], attr2))
                result = conn.fetchall()
                result1 = np.array(result)[:, 0]
                result2 = np.array(result)[:, 1]
                results[i] = np.corrcoef(result1, result2)[0][1]
        else:
            for i in range(len(attr1)):
                print("SELECT %s.%s, %s.%s FROM %s, %s WHERE %s.%s IS NOT NULL AND %s.%s IS NOT NULL" %
                            (table1, attr1[i], table2, attr2, table1, table2, table1, attr1[i], table2, attr2))
                conn.execute("SELECT %s.%s, %s.%s FROM %s, %s WHERE %s.%s IS NOT NULL AND %s.%s IS NOT NULL" %
                            (table1, attr1[i], table2, attr2, table1, table2, table1, attr1[i], table2, attr2))
                print('running')
                result = conn.fetchall()
                print(len(result))
                result1 = np.array(result)[:, 0]
                result2 = np.array(result)[:, 1]
                results[i] = np.corrcoef(result1, result2)[0][1]
                print(i, results)
    return results

def handle_condition(attr, table, condition):
    operator = ['=', '!=', '>', '<', '>=', '<=', 'not', 'and', 'or']
    comparison_operator = ['=', '!=', '>', '<', '>=', '<=']
    condition_operator = ['not', 'and', 'or']

    # print(condition)
    condition = Stack(infix_to_postfix(condition))
    # print(condition)

    attr_rtn = []
    duplication = Stack(condition.copy())
    for i in range(len(table)):
        # print(i, ':', table[i], attr[i], end=' ')
        stack = Stack(None)
        while condition.peek():
            c = condition.pop()
            if c not in operator:
                stack.push(c)
            elif c in condition_operator:
                if c == 'not':
                    operand = stack.pop()
                    stack.push(~operand)
                else:
                    operand1 = stack.pop()
                    operand2 = stack.pop()
                    if c == 'and':
                        stack.push(operand1 & operand2)
                    elif c == 'or':
                        stack.push(operand1 | operand2)
            elif c in comparison_operator:
                operand2 = aggregate(stack, table[i], attr[i])
                operand1 = aggregate(stack, table[i], attr[i])
                if c == '=':
                    stack.push(operand1 == operand2)
                elif c == '!=':
                    stack.push(operand1 != operand2)
                elif c == '>':
                    stack.push(operand1 > operand2)
                elif c == '<':
                    stack.push(operand1 < operand2)
                elif c == '>=':
                    stack.push(operand1 >= operand2)
                elif c == '<=':
                    stack.push(operand1 <= operand2)
        condition = Stack(duplication.copy())

        tmp = []
        results = stack.pop()
        # print(results)
        for j in range(len(results)):
            if results[j]:
                tmp.append(attr[i][j])
        attr_rtn.append(tmp)
    return attr_rtn

def process_selectA(cmd):
    attr = []
    
    cmdLower = cmd.lower()
    regex = cmd[cmdLower.find('selecta')+7:cmdLower.find('from')].strip()[1:-1]
    if cmdLower.find('where') != -1:
        table = [t.strip() for t in cmd[cmdLower.find('from')+4:cmdLower.find('where')].split(',')]
        conditionString = cmd[cmdLower.find('where')+5:]
    else:
        table = [t.strip() for t in cmd[cmdLower.find('from')+4:].split(',')]
        conditionString = None

    for t in table:
        attrTmp = []
        with sql.connect(host='localhost', user='root', password='root', db='information_schema') as conn:
            conn.execute("SELECT COLUMN_NAME FROM COLUMNS WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s'" % (usingDB, t))
            results = conn.fetchall()
            pattern = re.compile(regex)
            for r in results:
                if pattern.fullmatch(r[0]) != None:
                    attrTmp.append(r[0])
            attr.append(attrTmp)

    if conditionString != None:
        condition = []
        tmpString = ""
        for letter in conditionString:
            if letter == ' ' or letter == '\n':
                if len(tmpString) != 0:
                    condition.append(tmpString)
                    tmpString = ""
            elif letter == '(' or letter == ')':
                if len(tmpString) != 0:
                    condition.append(tmpString)
                    tmpString = ""
                condition.append(letter)
                if letter == ')' and len(condition) >= 4 and condition[-4].lower() == "cor":
                    tmpString = ''.join(condition[-4:])
                    for i in range(4):
                        condition.pop()
                    condition.append(tmpString)
                    tmpString = ""
            elif letter == '!' or letter == '<' or letter == '>':
                if len(tmpString) != 0:
                    condition.append(tmpString)
                tmpString = letter
            elif letter == '=':
                if tmpString == '!' or tmpString == '<' or tmpString == '>':
                    condition.append(tmpString+letter)
                else:
                    condition.append(tmpString)
                    condition.append(letter)
                tmpString = ""
            else:
                if tmpString == '!' or tmpString == '<' or tmpString == '>':
                    condition.append(tmpString)
                    tmpString = ""
                tmpString += letter
        if len(tmpString) != 0:
            condition.append(tmpString)
        # print(attr, table, condition)
        condition = [c.lower() for c in condition]
        attr = handle_condition(attr, table, condition)

    rtnList = []
    for i, t in enumerate(table):
        for a in attr[i]:
            rtnList.append("%s.%s" % (t, a))
    return ', '.join(rtnList)

def process_token(tokens):
    tmpString = ""
    while len(tokens) > 0:
        if tokens[-1] == ';':
            tmpString += ';'
            return tmpString
        elif tokens[-1] == '(':
            tokens.pop()
            if tokens[-1].lower() == "selecta":
                tmpString += "%s " % (process_token(tokens))
            else:
                tmpString += "( %s) " % (process_token(tokens))
        elif tokens[-1] == ')':
            tokens.pop()
            if tmpString.lower().find('selecta') == 0:
                tmpString = process_selectA(tmpString)
            return tmpString
        else:
            tmpString += "%s " % (tokens[-1])
            tokens.pop()

    return tmpString

def process_command(cmd):
    tokens = []
    tmpString = ""

    for letter in cmd:
        if letter == ' ' or letter == '\n':
            if len(tmpString) != 0:
                tokens.append(tmpString)
                tmpString = ""
        elif letter == '(' or letter == ')' or letter == ';':
            if len(tmpString) != 0:
                tokens.append(tmpString)
                tmpString = ""
            tokens.append(letter)
        else:
            tmpString += letter
    # print(tokens)

    # parse "use <database>;"
    if tokens[0].lower() == "use" and len(tokens) >= 2:
        global usingDB
        usingDB = tokens[1];

    cmd = process_token(tokens[::-1])
    # print(cmd)

    return cmd

def non_block_read(output):
    fd = output.fileno()
    flag = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)
    result = ""
    try:
        result = output.readline()
    except:
        pass
    fcntl.fcntl(fd, fcntl.F_SETFL, flag)
    return result

def main():
    try:
        proc = Popen(['mysql', '-f', '-t', '--unbuffered', '-uroot', '-proot'],
            stdin=PIPE, stdout=PIPE, stderr=subprocess.STDOUT)
        print(proc.stdout.readline().decode(), end="")
        while True:
            print("mysql> ",end="")
            cmd = ""
            while True:
                ori = input()
                cmd += '\n' + ori
                if ';' in ori:
                    break
                print("    -> ",end="")
            cmd = process_command(cmd) + '\n'

            if cmd.lower().find('selecta') == 0:
                printTable(process_selectA(cmd[:-2]))
            else:
                proc.stdin.write(cmd.encode());
                proc.stdin.flush()
                # print(proc.stdout.readline().decode(), end="")
                time.sleep(0.05)
                while True:
                    output = non_block_read(proc.stdout)
                    if not output:
                        break
                    print(output.decode(), end="")
                print("")
        proc.wait()

    finally:
        if proc.poll() == None:
            proc.terminate()

if __name__ == '__main__':
    main()
    # print(process_command("select (selecta '.*' from table where (cond<1 or cond>2) and cond=3) from table"))


