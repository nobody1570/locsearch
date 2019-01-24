from locsearch.localsearch.abstract_local_search import AbstractLocalSearch
from locsearch.termination.must_improve_termination_criterion \
    import MustImproveTerminationCriterion
from collections import namedtuple
from locsearch.aidfunc.is_improvement_func import bigger, smaller


class SteepestDescent(AbstractLocalSearch):
    """Performs a steepest descent algorithm on the given solution.

    Parameters
    ----------
    solution : AbstractLocalSearchSolution
        Contains all the data needed for the specific problem.
    minimise : bool, optional
        If the goal is to minimise the evaluation function, this should be
        True. If the goal is to maximise the evlauation function, this should
        be False. The default is True.

    Attributes
    ----------
    _solution : AbstractLocalSearchSolution
        Contains all the data needed for the specific problem.
    _termination_criterion : MustImproveTerminationCriterion
        Ends the algorithm if no more improvements can be found.
    _function
        The function used to determine if a delta value is better than another
        delta value.
    _best_found_delta_base_value : float
        Initialisation value for the delta value of each iteration. It's
        infinite when minimising or minus infinite when maximising.

    Examples
    --------
    An example of minimising:

    .. doctest::

        >>> import numpy
        >>> from locsearch.localsearch.steepestdescent.steepest_descent \\
        ...     import SteepestDescent
        >>> from locsearch.localsearch.move.tsp_array_swap import TspArraySwap
        >>> from locsearch.evaluation.tsp_evaluation_function \\
        ...     import TspEvaluationFunction
        >>> from locsearch.solution.tsp_solution import TspSolution
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
        ... # init SteepestDescent
        >>> steepest_descent = SteepestDescent(solution)
        ... # run algorithm
        >>> steepest_descent.run()
        Results(best_order=array([0, 1, 3, 2]), best_value=15)

    An example of maximising, note that the distance matrix is different:

    .. doctest::

        >>> import numpy
        >>> from locsearch.localsearch.steepestdescent.steepest_descent \\
        ...     import SteepestDescent
        >>> from locsearch.localsearch.move.tsp_array_swap import TspArraySwap
        >>> from locsearch.evaluation.tsp_evaluation_function \\
        ...     import TspEvaluationFunction
        >>> from locsearch.solution.tsp_solution import TspSolution
        ... # init solution
        >>> distance_matrix = numpy.array(
        ... [[0, 8, 5, 2],
        ...  [8, 0, 4, 7],
        ...  [5, 4, 0, 1],
        ...  [2, 7, 1, 0]])
        >>> size = distance_matrix.shape[0]
        >>> move = TspArraySwap(size)
        >>> evaluation = TspEvaluationFunction(distance_matrix, move)
        >>> solution = TspSolution(evaluation, move, size)
        ... # init SteepestDescent
        >>> steepest_descent = SteepestDescent(solution, False)
        ... # run algorithm
        >>> steepest_descent.run()
        Results(best_order=array([0, 1, 3, 2]), best_value=21)



    """

    def __init__(self, solution, minimise=True):
        super().__init__()

        self._solution = solution
        self._termination_criterion = \
            MustImproveTerminationCriterion(minimise)

        if minimise:
            self._function = smaller
            self._best_found_delta_base_value = float("inf")
        else:
            self._function = bigger
            self._best_found_delta_base_value = float("-inf")

    def run(self):
        """Starts running the steepest descent.

        Returns
        -------
        best_order : numpy.ndarray
            A one dimensional numpy array that contains the order of the
            points for the best found solution.
        best_value : int or float
            The best found value of the evaluation function. This should be
            the evaluation value of best_order.

        """

        # init solution
        base_value = self._solution.evaluate()
        self._solution.set_as_best(base_value)

        # init termination criterion
        self._termination_criterion.check_new_value(base_value)

        while self._termination_criterion.keep_running():

            # search the neighbourhood for the best move
            best_found_delta = self._best_found_delta_base_value
            best_found_move = None

            for move in self._solution.get_moves():

                # check quality move
                delta = self._solution.evaluate_move(move)

                # keep data best move
                if self._function(best_found_delta, delta):
                    best_found_delta = delta
                    best_found_move = move

            # check if the best_found_move improves the delta, if this is the
            # case perform the move and set a new best solution
            base_value = base_value + best_found_delta

            if self._termination_criterion.check_new_value(base_value):
                self._solution.move(best_found_move)
                self._solution.set_as_best(base_value)

        # return results

        Results = namedtuple('Results', ['best_order', 'best_value'])

        return Results(self._solution.best_order,
                       self._solution.best_order_value)
