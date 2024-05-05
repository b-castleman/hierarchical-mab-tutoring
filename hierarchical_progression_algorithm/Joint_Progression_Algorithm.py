import math

from .utils.progression_tree_creation import (
    makeProblemProgressionTrees,
    makeConceptProgressionTree,
)

from .mab_agents.ZPDES_Memory_CONCEPT import ZPDES_Memory_CONCEPT
from .mab_agents.ZPDES_Memory_PROBLEM import ZPDES_Memory_PROBLEM


class Joint_Progression_Algorithm(object):

    def __init__(
        self, curSection: str, problemsFilePath: str = "./instructor_data/problems.json"
    ):

        # Make Concept and Problem Progression Trees
        self.problemsFilePath = problemsFilePath

        self.progression_tree_concept = makeConceptProgressionTree(curSection)
        self.progression_tree_problem_dict, self.problemDifficulties = (
            makeProblemProgressionTrees(self)
        )

        # Make Overarching Concept MAB
        params_concept = {
            "history_length": 4,
            "progress_threshold": 0.74,
            "memory_threshold": math.exp(-12),
            "memory_multiplier": 10e10,
            "max_concept_attempts": 10,
            "min_concept_attempts": 2,
        }

        self.progression_algorithm_concept = ZPDES_Memory_CONCEPT(
            self.progression_tree_concept, params=params_concept
        )

        # Make all Problem MABs
        params_problem = {
            "history_length": 2,
            "progress_threshold": 0.74,
            "memory_threshold": math.exp(-12),
            "memory_multiplier": 10e10,
            "max_concept_attempts": 8,
            "min_concept_attempts": 1,
        }

        self.progression_algorithm_problem_dict = dict()

        all_concepts = self.progression_tree_concept.return_all_concepts()
        for concept in all_concepts:
            progression_tree_problem = self.progression_tree_problem_dict[concept]

            cur_concept_problem_difficulties = dict()

            all_problems = progression_tree_problem.return_all_concepts()

            for problem in all_problems:
                cur_concept_problem_difficulties[problem] = self.problemDifficulties[
                    problem
                ]

            self.progression_algorithm_problem_dict[concept] = ZPDES_Memory_PROBLEM(
                progression_tree_problem,
                params=params_problem,
                problem_difficulties=cur_concept_problem_difficulties,
            )

    def getCurrentQuestionId(self):
        """Gets the next question id given all previous data recorded"""

        # Check if the algorithm is complete
        concept_give = self.progression_algorithm_concept.get_current_problem()
        self.curConcept = concept_give

        if self.curConcept is None:
            return None, None

        # If there is an assigned concept, we have to proceed forth with another question. Consult the
        # corresponding problem MAB (given we now know the current concept) for the next question.
        problem_give = self.progression_algorithm_problem_dict[
            concept_give
        ].get_current_problem()
        self.curProblem = problem_give
        self.current_progression_algorithm_problem = (
            self.progression_algorithm_problem_dict[concept_give]
        )

        # If there are no problems left in this problem MAB, it means we've exhausted this concept's problems
        # despite not having "mastered" it (as the concept MAB doesn't think we're done). As a result, we
        # have to default to being complete since we have too few problems.
        if self.curProblem is None:
            # Delete problem from the frontier (mark it as mastered)
            self.progression_algorithm_concept.ZPD.remove(self.curConcept)
            self.progression_algorithm_concept.mastered_concepts.append(self.curConcept)

            # Obtain the next problem (this code should be refactored into it's own function in the future)
            initial_weight = (
                self.progression_algorithm_concept.params["initial_weight"]
                * self.progression_algorithm_concept.params["initial_weight_multiplier"]
            )
            for child in self.progression_algorithm_concept.children[self.curConcept]:
                can_add = True
                for prereq in self.progression_algorithm_concept.prereqs[child]:
                    if (
                        prereq
                        not in self.progression_algorithm_concept.mastered_concepts
                    ):
                        can_add = False

                if can_add:
                    self.progression_algorithm_concept.ZPD.append(child)
                    self.progression_algorithm_concept.weights_histories[child][
                        0
                    ] = initial_weight

            self.progression_algorithm_concept.length_ZPD = len(
                self.progression_algorithm_concept.ZPD
            )

            # Update the concept MAB for the next problem
            self.progression_algorithm_concept.new_problem()

            return self.getCurrentQuestionId()

        # All is good to return!
        return self.curConcept, self.curProblem

    def updateStudentCorrectness(self, student_answer_correctness):
        """Given a student's correctness to the current question, update the problem and concept MABs accordingly"""

        # Update concept MAB
        self.progression_algorithm_concept.student_answer_update(
            student_answer_correctness,
            difficulty=self.problemDifficulties[self.curProblem],
        )

        # Update problem MAB
        self.current_progression_algorithm_problem.student_answer_update(
            student_answer_correctness
        )
