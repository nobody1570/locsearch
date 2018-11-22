from locsearch.localsearch.abstract_local_search import AbstractLocalSearch
from locsearch.localsearch.acceptance.simulated_annealing_acceptance_function \
    import SimulatedAnnealingAcceptanceFunction
from collections import namedtuple


class SimulatedAnnealing(AbstractLocalSearch):
    """Performs a simulated annealing algorithm with the given parameters.

    Parameters
    ----------
    solution : AbstractLocalSearchSolution
        Contains all the data needed for the specific problem.
    termination_criterion : AbstractTerminationCriterion
        Implements a termination criterion to terminate the algorithm.
    cooling_function : AbstractCoolingFunction
        Implements the cooling function for the algorithm.
    iterations_for_temp_f : AbstrIterationsTempFunction
        Implements a function to determine the amount of iterations for a
        certain temperature.
    start_temperature : int, optional
        The starting temperature for the simulated annealing. The default is
        2000.

    Attributes
    ----------
    _solution : AbstractLocalSearchSolution
        Contains all the data needed for the specific problem.
    _termination_criterion : AbstractTerminationCriterion
        Implements a termination criterion to terminate the algorithm.
    _cooling_function : AbstractCoolingFunction
        Implements the cooling function for the algorithm.
    _iterations_for_temp_f : AbstrIterationsTempFunction
        Implements a function to determine the amount of iterations for a
        certain temperature.
    _temperature : int
        The current "temperature".
    _acceptance_function : SimulatedAnnealingAcceptanceFunction
        The acceptance function used.

    Examples
    --------
    A simple example:

    .. doctest::

        >>> import numpy
        >>> import random
        >>> from locsearch.localsearch.move.tsp_array_swap import TspArraySwap
        >>> from locsearch.localsearch.simulatedannealing.simulated_annealing \\
        ...     import SimulatedAnnealing
        >>> from locsearch.localsearch.simulatedannealing.geometric_cooling_function \\
        ...     import GeometricCoolingFunction
        >>> from locsearch.localsearch.simulatedannealing.cnst_iterations_temp_function \\
        ...     import CnstIterationsTempFunction
        >>> from locsearch.evaluation.tsp_evaluation_function \\
        ...     import TspEvaluationFunction
        >>> from locsearch.termination.min_temperature_termination_criterion \\
        ...     import MinTemperatureTerminationCriterion
        >>> from locsearch.solution.tsp_solution import TspSolution
        ... # seed random
        ... # (used here to always get the same output, this obviously is not
        ... #                                  needed in your implementation.)
        >>> random.seed(0)
        ... # init solution
        >>> distance_matrix = numpy.array(
        ... [[0, 2, 5, 8],
        ...  [2, 0, 4, 1],
        ...  [5, 4, 0, 7],
        ...  [8, 1, 7, 0]])
        >>> size = distance_matrix.shape[0]
        >>> move = TspArraySwap(size)
        >>> evaluation = TspEvaluationFunction(distance_matrix, move)
        >>> solution = TspSolution(evaluation, move, size)
        ... # init termination criterion
        >>> termination_criterion = MinTemperatureTerminationCriterion()
        ... # init cooling function
        >>> cooling_func = GeometricCoolingFunction()
        ... # init CnstIterationsTempFunction
        ... # (determines amount of itertions in function of the temperature)
        >>> i_for_temp = CnstIterationsTempFunction()
        ... # init SimulatedAnnealing
        >>> algorithm = SimulatedAnnealing(
        ...     solution, termination_criterion, cooling_func, i_for_temp)
        ... # run algorithm
        >>> algorithm.run()
        Results(best_order=array([0, 2, 3, 1]), best_value=15)

    """

    def __init__(self, solution, termination_criterion,
                 cooling_function, iterations_for_temp_f,
                 start_temperature=2000):
        super().__init__()

        self._solution = solution
        self._termination_criterion = termination_criterion
        self._cooling_function = cooling_function
        self._iterations_for_temp_f = iterations_for_temp_f
        self._temperature = start_temperature
        self._acceptance_function = SimulatedAnnealingAcceptanceFunction()

    def run(self):
        """Starts running the simulated annealing algorithm."""

        # init
        base_value = self._solution.evaluate()
        self._solution.set_as_best(base_value)

        self._termination_criterion.start_timing()

        # main loop
        while self._termination_criterion.keep_running():

            iterations = self._iterations_for_temp_f.get_iterations(
                self._temperature)

            # performs iterations at the current temperature
            #
            # it's basically a for loop that also terminates if the
            # termination criterion says it should.
            while iterations > 0 and \
                    self._termination_criterion.keep_running():

                # get and evaluate move
                move = self._solution.get_random_move()
                delta = self._solution.evaluate_move(move)

                # accept or reject move
                if delta <= 0:

                    # better than the current state --> accept
                    self._solution.move(move)
                    base_value = base_value + delta

                    # check if best state
                    if base_value < self._solution.best_order_value:
                        self._solution.set_as_best(base_value)

                else:

                    # worse than current state --> use acceptance function.
                    if self._acceptance_function.accept(
                            delta, self._temperature):

                        self._solution.move(move)
                        base_value = base_value + delta

                self._termination_criterion.iteration_done()
                iterations -= 1

            # lowers the current temperature
            self._temperature = self._cooling_function.next_temperature(
                self._temperature)

            self._termination_criterion.check_variable(self._temperature)

        # return results

        Results = namedtuple('Results', ['best_order', 'best_value'])

        return Results(self._solution.best_order,
                       self._solution.best_order_value)
