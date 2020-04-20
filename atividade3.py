from __future__ import print_function

from ortools.linear_solver import pywraplp


def main():
    solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # initial conditions - initial quantity of pieces
    initial_lot_1 = 0
    initial_lot_2 = 0

    # matrix with production costs
    # p[i, j]= production costs of standard j in month i 
    p = [
        [13, 9],  # Week1
        [10, 6],  # Week2
        [20, 8]   # Week3
    ]

    # matrix with stock costs
    # p[i, j]= stock costs of standard j in month i
    s = [
        [9, 7],  # Week1
        [9, 7],  # Week2
        [9, 7]   # Week3
    ]

    # matrix with demands
    # d[i,j]= demand of type j in month i 
    d = [
        [2000, 2000],  # Week1
        [1500, 1700],  # Week2
        [900,  1200]   # Week3
    ]

    n_weeks = len(p)
    n_cut_types = 2
    n_standards = 2

    # variables Xij
    # i -> week
    # j -> cut type
    x = {}
    for m in range(0, n_weeks):
        for n in range(0, n_standards):
            x[m, n] = solver.IntVar(0, solver.infinity(), 'week:%i type:%i' % (m+1, n+1))

    # matrix of amount of piences per week
    # r[i,j]= amount of type j in month i 
    r = [
        [x[0, 0] + 2 * x[0, 1] + initial_lot_1,                                                                         2 * x[0, 0] + 2 * x[0, 1] + initial_lot_2],
        [x[1, 0] + 2 * x[1, 1] + (x[0, 0] + 2 * x[0, 1] + initial_lot_1 - d[0][0]),                                     2 * x[1, 0] + 2 * x[1, 1] + (2 * x[0, 0] + 2 * x[0, 1] + initial_lot_2 - d[0][1])],
        [x[2, 0] + 2 * x[2, 1] + (x[1, 0] + 2 * x[1, 1] - d[1][0]) + (x[0, 0] + 2 * x[0, 1] + initial_lot_1 - d[0][0]), 2 * x[2, 0] + 2 * x[2, 1] + (2 * x[1, 0] + 2 * x[1, 1] - d[1][1] + 2 * x[0, 0] + 2 * x[0, 1] + initial_lot_2 - d[0][1])]
    ]

    # restrictions to attend demands
    for m in range(0, n_weeks):
        for n in range(0, n_cut_types):
            solver.Add(r[m][n] >= d[m][n])

    # matrix of production costs per standard
    # c[i,j]= production costs of standard j in month i 
    c = [
        [p[0][0] + 2*p[0][1], 2*p[0][0] + 2*p[0][1]],
        [p[1][0] + 2*p[1][1], 2*p[1][0] + 2*p[1][1]],
        [p[2][0] + 2*p[2][1], 2*p[2][0] + 2*p[2][1]]
    ]

    # matrix of stock type per month
    # e[i,j]= stock type j in month i 
    E = [
        [r[0][0] - d[0][0], r[0][1] - d[0][1]],
        [r[1][0] - d[1][0], r[1][1] - d[1][1]],
        [r[2][0] - d[2][0], r[2][1] - d[2][1]]
    ]

    # objective function - minimize costs
    # product of costs of standard for quantity + product of costs of type for quantity
    objective_function = 0
    for m in range(0, n_weeks):
        for n in range(0, n_cut_types):
            objective_function += (x[m, n] * c[m][n] + E[m][n] * s[m][n])

    solver.Minimize(objective_function)

    status = solver.Solve()

    # results
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())

        for i in range(0, n_weeks):
            for j in range(0, n_cut_types):
                print(x[i, j].name(), ' = ', x[i, j].solution_value())
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    main()
