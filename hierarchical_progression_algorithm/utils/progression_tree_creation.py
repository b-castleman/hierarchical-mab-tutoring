import json
from .tree import Static_Tree


def makeStaticTree(all_concepts, tree_structure):
    """Creates a static tree from all concepts and the overall tree structure"""
    concept_problems = dict()
    for concept in all_concepts:
        concept_problems[concept] = [concept]

    problem_components = {}
    for concept, concept_problems_list in concept_problems.items():
        for problem in concept_problems_list:
            problem_components[problem] = [problem]
    all_basic_components = list(problem_components.keys())

    return Static_Tree(
        children=tree_structure,
        all_concepts=all_concepts,
        concept_problems=concept_problems,
        all_basic_components=all_basic_components,
        problem_components=problem_components,
    )


def makeConceptProgressionTree(
    section,
    fn_concept_trees: str = "./hierarchical_progression_algorithm/instructor_data/concept_trees.json",
):
    """Obtain the progression tree from the section"""

    # Get the progression trees json file
    with open(fn_concept_trees) as json_file:
        tree_structure_dict = json.load(json_file)

    if section not in tree_structure_dict:
        raise Exception("Section is not valid!")

    # Obtain the correct tree
    tree_structure = tree_structure_dict[section]

    # Make a list of all possible concepts
    all_concepts = list(tree_structure.keys())
    all_concepts.remove("Root")

    # Create tree
    return makeStaticTree(all_concepts, tree_structure)


def makeProblemProgressionTrees(joint_progression_algorithm):
    """Create all problem progression tree for every concept"""

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
