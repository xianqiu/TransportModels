from transportmodels import Transport, TransModel


def example1():
    t = Transport()
    t.set_supplies([200, 250])
    t.set_demands([100, 150, 200])
    t.set_cost_matrix([[90, 70, 100], [80, 65, 75]])
    t.solve()

    print(">>> Example 1: Solve the balanced transportation problem.")
    print("solution: ", t.get_solution())
    print("objective value: ", t.get_objective_value())
    print("is optimal: ", t.is_solution_optimal())


def example2():
    quota_vectors = [[5, 7, 3, -7, -3, -5],
                     [5, -7, 3, 7, -3, -5],
                     [5, 7, -3, -7, 3, -5],
                     [-5, 7, 3, -7, -3, 5]
                     ]

    cost_matrix = [[0, 0, 0, 3, 1, 100], [0, 0, 0, 4, 2, 4], [0, 0, 0, 100, 3, 3],
                   [3, 4, 100, 0, 0, 0], [1, 2, 3, 0, 0, 0], [100, 4, 3, 0, 0, 0]]

    print(">>> Example 2: Solve a batch of the balanced transportation problems, using multiple processors.")

    t = TransModel()
    t.set_processors(2)
    t.set_quota_vectors(quota_vectors)
    t.set_cost_matrix(cost_matrix)
    t.solve()
    solutions = t.get_solutions()
    objectives = t.get_objective_values()

    for i in range(len(solutions)):
        print("--- problem %d ---" % i)
        print("solution", solutions[i])
        print("objective value", objectives[i])


if __name__ == '__main__':
    example1()
    example2()
