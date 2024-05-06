import json


class Base_Tree(object):
    def return_parents(self):
        # a method to return a dictionary where the keys are node names and the values are a list of the names of the immediate parents of the node
        pass

    def return_all_ancestors(self):
        # a method to return a dictionary where the keys are node names and the values are a list of the names of all the ancestors of the node
        pass

    def return_children(self):
        # a method to return a dictionary where the keys are node names and the values are a list of the names of the immediate childre of the node
        pass

    def return_all_descendants(self):
        # a method to return a dictionary where the keys are node names and the values are a list of all the descendants parents of the node
        pass

    def return_all_concepts(self):
        # a method to return a list of all the possible concepts
        pass

    def return_all_basic_components(self):
        # a method to return a list of all possible components
        pass

    def return_concept_problems(self):
        # a method to return a dictionary where the keys are concept names and the values are a list of all problems corresponding to that concept
        pass

    def return_problem_components(self):
        # a method to return a dictionary where the keys are problems and the values are a list of all components corresponding to that problem
        pass

    def save_tree(self):
        # a method for saving the tree to file
        pass


class Static_Tree(
    Base_Tree
):  # can either load in using a json string representation or rebuild from a dictionary of children
    def __init__(
        self,
        tree_filename=None,
        children=None,
        all_concepts=None,
        concept_problems=None,
        all_basic_components=None,
        problem_components=None,
    ):
        if tree_filename is not None:
            with open(tree_filename, "r") as text_file:
                tree_json_str = text_file.readlines()[0]

            (
                self.children,
                self.all_descendants,
                self.parents,
                self.all_ancestors,
                self.all_concepts,
                self.concept_problems,
                self.all_basic_components,
                self.problem_components,
            ) = json.loads(tree_json_str)
        else:
            self.children = children  # dict - keys: concept, values: list of immediate children of the concept
            self.all_concepts = all_concepts  # list: list of all concepts, each item in the list must be hashable
            self.concept_problems = concept_problems  # dict keys: concept, values: list of problems corresponding to the concept
            self.all_basic_components = all_basic_components  # list: All basic components that make up each problem (if no shared components between problems, they can be the same as the list of all problems)
            self.problem_components = problem_components = (
                problem_components  # dict: keys: problem, values: list of basic the problem consists of
            )
            self.all_descendants = {}
            self.parents = {}
            self.all_ancestors = {}
            self._calculate_all_descendants("Root")
            self._calculate_parents()
            for concept in self.all_concepts:
                if len(self.children[concept]) == 0:
                    self._calculate_all_ancestors(concept)

    def _calculate_all_descendants(self, concept):
        if concept not in self.all_descendants:
            all_descendants = set()

            for child_concept in self.children[concept]:
                all_descendants.update(self._calculate_all_descendants(child_concept))
                all_descendants.add(child_concept)

            self.all_descendants[concept] = list(all_descendants)
        return self.all_descendants[concept]

    def _calculate_parents(self):
        for concept in self.all_concepts:
            self.parents[concept] = []
        for concept in self.all_concepts:
            for child_concept in self.children[concept]:
                if concept not in self.parents[child_concept]:
                    self.parents[child_concept].append(concept)

    def _calculate_all_ancestors(self, concept):
        if concept not in self.all_ancestors:
            all_ancestors = set()

            for parent_concept in self.parents[concept]:
                all_ancestors.update(self._calculate_all_ancestors(parent_concept))
                all_ancestors.add(parent_concept)

            self.all_ancestors[concept] = list(all_ancestors)
        return self.all_ancestors[concept]

    def string_tree(self):
        return json.dumps(
            (
                self.children,
                self.all_descendants,
                self.parents,
                self.all_ancestors,
                self.all_concepts,
                self.concept_problems,
                self.all_basic_components,
                self.problem_components,
            )
        )

    def save_tree(self, tree_filename):
        with open(tree_filename, "w") as text_file:
            text_file.write(self.string_tree())

    def return_parents(
        self,
    ):  # return the parents dict (a dictionary where the keys are node names and the values are a list of the names of the immediate parents of the node)
        return self.parents

    def return_all_ancestors(
        self,
    ):  # return the all_ancestors dict (a dictionary where the keys are node names and the values are a list of the names of all the ancestors of the node)
        return self.all_ancestors

    def return_children(
        self,
    ):  # return the children_names dict (a dictionary where the keys are node names and the values are a list of the names of the immediate childre of the node)
        return self.children

    def return_all_descendants(
        self,
    ):  # return the all_descendants_names dict (a dictionary where the keys are node names and the values are a list of all the descendants parents of the node)
        return self.all_descendants

    def return_all_concepts(self):
        return self.all_concepts

    def return_all_basic_components(self):
        # a method to return a list of all possible components
        return self.all_basic_components

    def return_concept_problems(self):
        # a method to return a dictionary where the keys are concept names and the values are a list of all problems corresponding to that concept
        return self.concept_problems

    def return_problem_components(self):
        # a method to return a dictionary where the keys are problems and the values are a list of all components corresponding to that problem
        return self.problem_components

    def add_edges_to_progression(self, progression_graph):
        # Add directed edges between parents and children to a graphviz graph for visualization purporses
        for node_name, node_children in self.children.items():
            for child_name in node_children:
                progression_graph.edge(node_name, child_name, contraint="true")
