import re

from flask import Flask, request
from flask.templating import render_template
import sympy


app = Flask(__name__)

def row_switch(n, i, j):

    r = sympy.eye(n)
    r[i, i] = 0
    r[j, j] = 0
    r[i, j] = 1
    r[j, i] = 1
    return r


def row_multiply(n, i, c):

    r = sympy.eye(n)
    r[i, i] = c
    return r


def row_add(n, i, j, c):

    r = sympy.eye(n)
    r[i, j] = c
    return r


def simplification(a):

    r = r'\begin{align*}'
    r += sympy.latex(a)
    m = len(a.col(0))
    n = len(a.row(0))
    i = 0
    j = 0
    while i < m and j < n:
        if j >= n:
            break
        if a[i, j].is_zero:
            for ii in range(i + 1, m):
                if not a[ii, j].is_zero:
                    a = row_switch(m, i, ii) * a
                    r += r'&\to' + sympy.latex(a) + r'\\'
                    break
            else:
                j += 1
                continue
        pivot = a[i, j]
        if pivot != sympy.sympify(1):
            a = row_multiply(m, i, 1 / pivot) * a
            r += r'&\to' + sympy.latex(a) + r'\\'
        flag = False
        for ii in range(m):
            if i != ii and not a[ii, j].is_zero:
                a = row_add(m, ii, i, -a[ii, j]) * a
                flag = True
        if flag:
            r += r'&\to' + sympy.latex(a) + r'\\'
        i += 1
        j += 1
    r += r'\end{align*}'
    return r


@app.route('/', methods=['GET'])
def main_page():
    row_num = int(request.args.get('row-num', '3'))
    col_num = int(request.args.get('col-num', '3'))
    return render_template('index.html', row_num=row_num, col_num=col_num, input_mat=[[0] * col_num] * row_num, result='')


@app.route('/', methods=['POST'])
def main_post():
    row_num = int(request.form.get('row-num', '3'))
    col_num = int(request.form.get('col-num', '3'))
    input_mat = []
    flag = False
    for i in range(row_num):
        l = []
        for j in range(col_num):
            element = request.form.get(f'input-mat[{i}][{j}]')
            if not re.fullmatch(r'[a-zA-Z0-9\+\-\*\/\.]+', element):
                flag = True
            l.append(element)
        input_mat.append(l)
    if flag:
        return render_template('index.html', row_num=row_num, col_num=col_num, input_mat=input_mat, result='要素が空か，使用できない文字が含まれています．')
    m = sympy.Matrix(input_mat)
    result = simplification(m)
    return render_template('index.html', row_num=row_num, col_num=col_num, input_mat=input_mat, result='\\[' + result + '\\]')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)