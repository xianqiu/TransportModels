# bankrupt


Installation
---------------

Use one of the following method:

* pip install
```bash
pip --install bankrupt
pip --install bankrupt --upgrade
```
* clone repository and install with:
```bash
python setup.py install
```        
Usage
-------

* Solve the balanced transportation problem.

```python
from transportmodels import Transport
t = Transport()
t.set_supplies([200, 250])
t.set_demands([100, 150, 200])
t.set_cost_matrix([[90, 70, 100], [80, 65, 75]])
t.solve()
print(t.get_solution())
print(t.get_objective_value())
```

* Solve a batch of the balanced transportation problem, using multiple processors.

```python
from transportmodels import TransModel
# data
quota_vectors = [[5, 7, 3, -7, -3, -5],
                     [5, -7, 3, 7, -3, -5],
                     [5, 7, -3, -7, 3, -5],
                     [-5, 7, 3, -7, -3, 5]
                     ]

cost_matrix = [[0, 0, 0, 3, 1, 100], [0, 0, 0, 4, 2, 4], [0, 0, 0, 100, 3, 3],
               [3, 4, 100, 0, 0, 0], [1, 2, 3, 0, 0, 0], [100, 4, 3, 0, 0, 0]]
# solver
t = TransModel()
t.set_processors(2)
t.set_quota_vectors(quota_vectors)
t.set_cost_matrix(cost_matrix)
t.solve()
# solutions and objective values
solutions = t.get_solutions()
objective_values = t.get_objective_values()
# print info
for i in range(len(solutions)):
    print("--- problem %d ---" % i)
    print("solution", solutions[i])
    print("objective value", objective_values[i])
```