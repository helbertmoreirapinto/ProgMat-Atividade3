from __future__ import print_function

from ortools.linear_solver import pywraplp


def main():
    solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # initial conditions
    initial_lot_1 = 0
    initial_lot_2 = 0

    # matrix with production costs
    p = [
        [13, 9],  # week1
        [10, 6],  # week2
        [20, 8]  # week3
    ]

    # matrix with stock costs
    s = [
        [9, 7],  # week1
        [9, 7],  # week2
        [9, 7]  # week3
    ]

    # matrix with demands
    d = [
        [2000, 2000],  # week1
        [1500, 1700],  # week2
        [900, 1200]  # week3
    ]

    n_weeks = len(p)
    n_cut_types = 2

    # variables Xij
    # i -> week
    # j -> cut type
    x = {}
    for m in range(0, n_weeks):
        for n in range(0, n_cut_types):
            x[m, n] = solver.IntVar(0, solver.infinity(), 'week:%i type:%i' % (m+1, n+1))

    # production week
    r = [
        [x[0, 0] + 2 * x[0, 1] + initial_lot_1, 2 * x[0, 0] + 2 * x[0, 1] + initial_lot_2],
        [x[1, 0] + 2 * x[1, 1] + (x[0, 0] + 2 * x[0, 1] - d[0][0]), 2 * x[1, 0] + 2 * x[1, 1] + (2 * x[0, 0] + 2 * x[0, 1] - d[0][1])],
        [x[2, 0] + 2 * x[2, 1] + (x[0, 0] + 2 * x[0, 1] - d[0][0]) + (x[1, 0] + 2 * x[1, 1] - d[1][0]), 2 * x[2, 0] + 2 * x[2, 1] + (2 * x[0, 0] + 2 * x[0, 1] - d[0][1]) + (2 * x[1, 0] + 2 * x[1, 1] - d[1][1])]
    ]

    # restrictions
    for m in range(0, n_weeks):
        for n in range(0, n_cut_types):
            solver.Add(r[m][n] >= d[m][n])

    # matrix production costs
    c = [
        [p[0][0] + 2 * p[0][1], 2 * p[0][0] + 2 * p[0][1]],
        [p[1][0] + 2 * p[1][1], 2 * p[1][0] + 2 * p[1][1]],
        [p[2][0] + 2 * p[2][1], 2 * p[2][0] + 2 * p[2][1]]
    ]

    # matrix stock costs
    e = [
        [r[0][0] - d[0][0], r[0][1] - d[0][1]],
        [r[1][0] - d[1][0], r[1][1] - d[1][1]],
        [r[2][0] - d[2][0], r[2][1] - d[2][1]]
    ]

    # objective function
    objective_function = 0
    for m in range(0, n_weeks):
        for n in range(0, n_cut_types):
            objective_function += (x[m, n] * c[m][n] + s[m][n] * e[m][n])

    solver.Minimize(objective_function)

    status = solver.Solve()

    # results
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Minimum cost = ', solver.Objective().Value())

        for i in range(0, n_weeks):
            for j in range(0, n_cut_types):
                print(x[i, j].name(), ' = ', x[i, j].solution_value())
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    main()
