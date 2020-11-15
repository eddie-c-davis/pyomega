# tests/test_visit.py
import sys
import ast

sys.path.append("./src")
from pyomega.parser import Parser
from pyomega.visit import CodeGenVisitor


def codegen_test(expr):
    space = Parser(expression=expr).parse()
    visitor = CodeGenVisitor()
    source = visitor(space)
    assert source == expr


def test_2d():
    expr = "s2d = {[i, j]: 0 <= i < N ^ 0 <= j < M}"
    codegen_test(expr)


def test_3d():
    expr = "s3d = {[i, j, k]: 0 <= i < N ^ 0 <= j < M ^ 0 <= k < K}"
    codegen_test(expr)


def test_spmv():
    # Omega Code
    # symbolic N,col(2),rp(1),rp1(1);
    # Icsr := {[i,n,j]:j-col(i,n)=0&&i>=0&&n-rp(i)>=0&&N-1>=0&&-i+N-1>=0&&-n+rp1(i)-1>=0&&-rp(i)+rp1(i)-1>=0};
    # codegen(Icsr) given {[i,n,j]: N-1>=0&&-rp(i)+rp1(i)-1>=0};
    expr = "spmv = {[i, n, j]: 0 <= i < N ^ rp(i) <= n < rp(i + 1) ^ j == col(n)}"
    codegen_test(expr)


def test_krp():
    expr = "krp = {[n, i, j, k, r]: 0 <= n < M ^ i == ind0(n) ^ j == ind1(n) ^ k == ind2(n) ^ 0 <= r < R}"
    # expr = "krp = {[p, i, q, j, n, k, r]: 0 <= p < F ^ i == ind0(p) ^ pos0(p) <= q < pos0(p+1) ^ j == ind1(q) ^ pos1(q) <= n < pos1(q+1) ^ k == ind2(n) ^ 0 <= r < R}"
    # Omega Code:
    # symbolic M,R,ind0(1),ind1(1),ind2(1);
    # krp := {[n,i,j,k,r]:i-ind0(n)=0&&j-ind1(n)=0&&k-ind2(n)=0&&n>=0&&r>=0&&M-1>=0&&R-1>=0&&-n+M-1>=0&&-r+R-1>=0};
    # r0krp := {[n,i,j,k,r] -> [0,n,0,i,0,j,0,k,0,r,0]};
    # codegen r0krp:krp given {[n,i,j,k,r]: M-1>=0&&R-1>=0};
    codegen_test(expr)