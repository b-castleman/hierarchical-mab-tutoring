import json
from .tree import Static_Tree, Build_Tree_Data


def makeStaticTree(all_concepts, tree_structure):
    concept_problems = dict()
    for concept in all_concepts:
        concept_problems[concept] = [concept]

    problem_components = {}
    for concept, concept_problems_list in concept_problems.items():
        for problem in concept_problems_list:
            problem_components[problem] = [problem]
    all_basic_components = list(problem_components.keys())

    data = Build_Tree_Data(
        all_concepts=all_concepts,
        concept_problems=concept_problems,
        all_basic_components=all_basic_components,
        problem_components=problem_components,
        n=1,
    )

    return Static_Tree(
        children=tree_structure,
        all_concepts=all_concepts,
        concept_problems=concept_problems,
        all_basic_components=all_basic_components,
        problem_components=problem_components,
    )


def makeProblemProgressionTrees(joint_progression_algorithm):

    progression_tree_problem_dict = dict()
    problem_difficulties = dict()

    all_concepts = (
        joint_progression_algorithm.progression_tree_concept.return_all_concepts()
    )

    with open(joint_progression_algorithm.problemsFilePath) as json_file:
        problemsDict = json.load(json_file)

    for concept in all_concepts:
        problemList = problemsDict[concept]

        # Define tree necessities
        all_problems = []
        tree_structure = {"Root": []}

        for problem in problemList:
            id = problem["id"]
            difficulty = problem["difficulty"]

            problem_difficulties[id] = difficulty

            all_problems.append(id)
            tree_structure["Root"].append(id)
            tree_structure[id] = []

        curProblemProgressionTree = makeStaticTree(all_problems, tree_structure)
        progression_tree_problem_dict[concept] = curProblemProgressionTree

    return progression_tree_problem_dict, problem_difficulties
