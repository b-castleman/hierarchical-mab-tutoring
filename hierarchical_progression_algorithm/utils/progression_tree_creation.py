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


def makeConceptProgressionTree(section):
    all_concepts = []
    if section == "ai_intro_and_defs":
        all_concepts.extend(["ai_definitions", "four_schools_of_thought"])

        tree_structure = {
            "Root": ["ai_definitions"],
            "ai_definitions": ["four_schools_of_thought"],
            "four_schools_of_thought": [],
        }

    elif section == "turing_test":
        all_concepts.extend(["turing_test_definition", "turing_test_examples"])

        tree_structure = {
            "Root": ["turing_test_definition"],
            "turing_test_definition": ["turing_test_examples"],
            "turing_test_examples": [],
        }

    elif section == "applications_of_ai":
        all_concepts.extend(["applications_of_ai_examples"])

        tree_structure = {
            "Root": ["applications_of_ai_examples"],
            "applications_of_ai_examples": [],
        }
    elif section == "history_of_ai":
        all_concepts.extend(
            [
                "gestation_and_early_enthusiasm_era",
                "knowledge_based_era",
                "ai_becomes_scientific",
            ]
        )

        tree_structure = {
            "Root": ["gestation_and_early_enthusiasm_era"],
            "gestation_and_early_enthusiasm_era": ["knowledge_based_era"],
            "knowledge_based_era": ["ai_becomes_scientific"],
            "ai_becomes_scientific": [],
        }
    elif section == "logical_agents":
        all_concepts.extend(["wumpus_specific", "logic_review"])

        tree_structure = {
            "Root": ["wumpus_specific", "logic_review"],
            "logic_review": [],
            "wumpus_specific": [],
        }
    elif section == "rational_agents":
        all_concepts.extend(["acting_rationally", "peas", "environment_types"])

        tree_structure = {
            "Root": ["acting_rationally"],
            "acting_rationally": ["peas", "environment_types"],
            "peas": [],
            "environment_types": [],
        }
    elif section == "search":
        all_concepts.extend(
            [
                "search_definition",
                "simple_search",
                "constraint_search",
                "adversarial_search",
                "delete_later_sub",
            ]
        )

        tree_structure = {
            "Root": ["search_definition"],
            "search_definition": [
                "simple_search",
                "constraint_search",
                "adversarial_search",
            ],
            "adversarial_search": ["delete_later_sub"],
            "simple_search": ["delete_later_sub"],
            "constraint_search": ["delete_later_sub"],
            "delete_later_sub": [],
        }
    elif section == "ml_intro":
        all_concepts.extend(["ml_basic_concepts"])
        tree_structure = {"Root": ["ml_basic_concepts"], "ml_basic_concepts": []}
    elif section == "perceptron":
        all_concepts.extend(["perceptron_qs"])
        tree_structure = {"Root": ["perceptron_qs"], "perceptron_qs": []}
    else:
        raise Exception("Invalid section")

    return makeStaticTree(all_concepts, tree_structure)


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
