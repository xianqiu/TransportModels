import multiprocessing
from ortools.linear_solver import pywraplp


class Transport(object):
    """ Solve the balanced transportation problem.
    """

    def __init__(self):
        self.__solver = pywraplp.Solver('BalancedTransport', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
        self.__a = []  # supplies
        self.__m = 0
        self.__b = []  # demands
        self.__n = 0
        self.__c = None  # cost matrix
        self.__x = None  # decision variables
        self.__obj = None  # objective
        self.__solution = None
        self.__obj_value = None
        self.__status = None  # solver status

    def __init_variables(self):
        self.__x = [None] * self.__m
        for i in range(self.__m):
            self.__x[i] = [None] * self.__n
            for j in range(self.__n):
                self.__x[i][j] = self.__solver.NumVar(0, self.__solver.infinity(), 'x%d%d' % (i, j))

    def __init_constraints(self):
        ct_supply = [None] * self.__m
        for i in range(self.__m):
            ct_supply[i] = self.__solver.Constraint(self.__a[i], self.__a[i])
            for j in range(self.__n):
                ct_supply[i].SetCoefficient(self.__x[i][j], 1.0)

        ct_demand = [None] * self.__n
        for j in range(self.__n):
            ct_demand[j] = self.__solver.Constraint(self.__b[j], self.__b[j])
            for i in range(self.__m):
                ct_demand[j].SetCoefficient(self.__x[i][j], 1.0)

    def __init_objective(self):
        self.__obj = self.__solver.Objective()
        for i in range(self.__m):
            for j in range(self.__n):
                self.__obj.SetCoefficient(self.__x[i][j], self.__c[i][j])
        self.__obj.SetMinimization()

    @staticmethod
    def __assert_nonempty_list(x):
        if not x:
            raise ValueError("input cannot be empty!")
        elif not isinstance(x, list):
            raise ValueError("input must be a list!")

    def set_supplies(self, supplies):
        """
        :param supplies: a list of numbers.
        """
        self.__assert_nonempty_list(supplies)
        self.__a = supplies
        self.__m = len(self.__a)

    def set_demands(self, demands):
        """
        :param demands: a list of numbers.
        """
        self.__assert_nonempty_list(demands)
        self.__b = demands
        self.__n = len(self.__b)

    def set_cost_matrix(self, cost_matrix):
        """
        :param cost_matrix: an m by n matrix (2d list),
            where m = size of supplies and n = size of demands.
        """
        if not self.__m or not self.__n:
            raise ValueError("set supplies and demands first!")
        else:
            m = len(cost_matrix)
            n = len(cost_matrix[0])
            if m != self.__m or n != self.__n:
                raise ValueError("cost matrix has wrong dimension!")

        self.__c = cost_matrix

    def __check_parameters(self):
        if not self.__m or not self.__n or not self.__c:
            raise ValueError("Set parameters first!")
        # check whether supplies meet demands
        if sum(self.__a) != sum(self.__b):
            raise ValueError("Supplies do not meet demands!")

    def solve(self):
        self.__check_parameters()
        self.__init_variables()
        self.__init_constraints()
        self.__init_objective()
        self.__status = self.__solver.Solve()
        self.__solution = [None] * self.__m
        for i in range(self.__m):
            self.__solution[i] = [None] * self.__n
            for j in range(self.__n):
                self.__solution[i][j] = self.__x[i][j].solution_value()
        self.__obj_value = self.__obj.Value()

    def get_solution(self):
        return self.__solution

    def get_objective_value(self):
        return self.__obj_value

    def is_solution_optimal(self):
        return True if self.__status == self.__solver.OPTIMAL else False


class __TransportB(object):
    """ Solve a batch of the transportation problems.
    """

    def __init__(self):
        self.__c = None  # cost matrix
        self.__quota_vectors = None  # quota vectors
        self.__batch_size = 0
        self.__solutions = None
        self.__objective_values = None

    def set_cost_matrix(self, cost_matrix):
        """
        :param cost_matrix: an n by n square matrix (2d list),
            where n = size of each quota vector.
        :return:
        """
        if not self.__batch_size:
            raise ValueError("set quota vectors first!")
        else:
            n1 = len(cost_matrix)
            n2 = len(cost_matrix[0])
            if n1 != n2 or n1 != len(self.__quota_vectors[0]):
                print(n1, n2, self.__batch_size)
                raise ValueError("cost matrix has wrong dimension!")

        self.__c = cost_matrix

    def set_quota_vectors(self, quota_vectors):
        """
        :param quota_vectors: a list of vectors (2d list),
            where each quota vector contains supplies or demands, i.e. positive value stands for supply,
            and negative value stands for demand.
        :return:
        """
        if not quota_vectors:
            raise ValueError("quota vector cannot be empty!")
        if not isinstance(quota_vectors[0], list):
            quota_vectors = [quota_vectors]
        if not isinstance(quota_vectors, list) or not isinstance(quota_vectors[0], list):
            raise ValueError("quota vector must be a list!")

        self.__quota_vectors = quota_vectors
        self.__batch_size = len(self.__quota_vectors)

    @staticmethod
    def __parse_quota_vector(vec):
        size = len(vec)
        a = [0] * size
        a_index = [0] * size
        b = [0] * size
        b_index = [0] * size
        i_a = 0
        i_b = 0
        for i in range(size):
            if vec[i] > 0:
                a_index[i_a] = i
                a[i_a] = vec[i]
                i_a += 1
            elif vec[i] < 0:
                b_index[i_b] = i
                b[i_b] = -vec[i]
                i_b += 1
        return a, a_index, b, b_index

    def __parse_matrix(self, a_index, b_index):
        # parse cost matrix
        m = len(a_index)
        n = len(b_index)
        cost_matrix = [None] * m
        for i in range(m):
            cost_matrix[i] = [0] * n
            for j in range(n):
                cost_matrix[i][j] = self.__c[a_index[i]][b_index[j]]
        return cost_matrix

    @staticmethod
    def __trans_solve(a, b, c):
        trans = Transport()
        trans.set_supplies(a)
        trans.set_demands(b)
        trans.set_cost_matrix(c)
        trans.solve()
        return trans.get_solution(), trans.get_objective_value()

    def __check_parameters(self):
        if not self.__batch_size or not self.__c:
            raise ValueError("Set parameters first!")

    def solve(self):
        self.__check_parameters()
        self.__solutions = [None] * self.__batch_size
        self.__objective_values = [0.0] * self.__batch_size
        i = 0
        for quota in self.__quota_vectors:
            a, a_index, b, b_index = self.__parse_quota_vector(quota)
            c = self.__parse_matrix(a_index, b_index)
            self.__solutions[i], self.__objective_values[i] = self.__trans_solve(a, b, c)
            i += 1

    def get_solutions(self):
        return self.__solutions[0] if self.__batch_size == 1 else self.__solutions

    def get_objective_values(self):
        return self.__objective_values[0] if self.__batch_size == 1 else self.__objective_values


def solve_transport_batch(quota_vectors, cost_matrix):
    t = __TransportB()
    t.set_quota_vectors(quota_vectors)
    t.set_cost_matrix(cost_matrix)
    t.solve()
    return t.get_solutions(), t.get_objective_values()


class TransportBP(object):

    def __init__(self):
        self.__proc = 1  # number of processors
        self.__c = None  # cost matrix
        self.__quotas = None
        self.__batch_size = 0
        self.__partitions = None
        self.__solutions = None
        self.__objective_values = None

    def set_processors(self, proc):
        assert isinstance(proc, int) and proc > 0, \
            ValueError("processor number must be a positive integer!")
        self.__proc = min(proc, multiprocessing.cpu_count())

    def __make_partitions(self):
        partition_number = min(self.__batch_size, self.__proc)
        partition_size = self.__batch_size // self.__proc
        self.__partitions = [None] * partition_number
        for i in range(partition_number):
            self.__partitions[i] = self.__quotas[i * partition_size: (i + 1) * partition_size]
        if self.__batch_size % self.__proc:
            self.__partitions[partition_number-1] += self.__quotas[partition_number*partition_size:]

    def set_cost_matrix(self, cost_matrix):
        self.__c = cost_matrix

    def set_quota_vectors(self, quota_vectors):
        if not quota_vectors:
            raise ValueError("quota vector cannot be empty!")
        if not isinstance(quota_vectors[0], list):
            quota_vectors = [quota_vectors]
        if not isinstance(quota_vectors, list) or not isinstance(quota_vectors[0], list):
            raise ValueError("quota vector must be a list!")

        self.__quotas = quota_vectors
        self.__batch_size = len(self.__quotas)

    def solve(self):
        self.__make_partitions()
        pool = multiprocessing.Pool(processes=self.__proc)
        result = []
        for part in self.__partitions:
            result.append(pool.apply_async(solve_transport_batch, (part, self.__c)))
        pool.close()
        pool.join()

        self.__solutions = []
        self.__objective_values = []
        for res in result:
            solutions, objective_values = res.get()
            if not isinstance(objective_values, list):
                solutions = [solutions]
                objective_values = [objective_values]
            self.__solutions += solutions
            self.__objective_values += objective_values

    def get_solutions(self):
        return self.__solutions[0] if self.__batch_size == 1 else self.__solutions

    def get_objective_values(self):
        return self.__objective_values[0] if self.__batch_size == 1 else self.__objective_values


TransModel = TransportBP
