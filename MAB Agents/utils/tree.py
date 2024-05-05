import numpy as np
import json
from graphviz import Digraph
import pickle
import compare_functions

def remove_item(item_list, item):
    if item in item_list:
        item_list.remove(item)
    return list(item_list)

def create_ngrams(trace, n):
    #A function that returns a list of n-grams of a trace
    return [trace[i:i+n] for i in range(len(trace)-n+1)]

class Build_Tree_Data(object):
    def __init__(self, all_concepts, concept_problems, all_basic_components, problem_components, n = 1, data = {'traces': {},'traces_ngrams': {}}):
        self.all_concepts = all_concepts
        self.concept_problems = concept_problems
        self.all_basic_components = all_basic_components
        self.problem_components = problem_components
        self.data = data
        self.data['traces']['Root'] = ''
        self.data['traces_ngrams']['Root'] = []
        self.n = n

class Base_Tree(object):
    def return_parents(self):
        # a method to return a dictionary where the keys are node names and the values are a list of the names of the immediate parents of the node
        pass

    def return_all_ancestors(self): 
        #a method to return a dictionary where the keys are node names and the values are a list of the names of all the ancestors of the node
        pass

    def return_children(self): 
        #a method to return a dictionary where the keys are node names and the values are a list of the names of the immediate childre of the node
        pass

    def return_all_descendants(self): 
        #a method to return a dictionary where the keys are node names and the values are a list of all the descendants parents of the node
        pass

    def return_all_concepts(self):
        #a method to return a list of all the possible concepts
        pass

    def return_all_basic_components(self):
        #a method to return a list of all possible components
        pass

    def return_concept_problems(self):
        #a method to return a dictionary where the keys are concept names and the values are a list of all problems corresponding to that concept
        pass

    def return_problem_components(self):
        #a method to return a dictionary where the keys are problems and the values are a list of all components corresponding to that problem
        pass
    def save_tree(self):
        #a method for saving the tree to file
        pass


class Static_Tree(Base_Tree): #can either load in using a json string representation or rebuild from a dictionary of children
    def __init__(self, tree_filename = None, children = None, all_concepts = None, concept_problems = None, 
        all_basic_components = None, problem_components = None):
        if tree_filename is not None:
            with open (tree_filename, "r") as text_file:
                tree_json_str = text_file.readlines()[0]

            self.children, self.all_descendants, self.parents, self.all_ancestors, \
            self.all_concepts, self.concept_problems, self.all_basic_components, self.problem_components = json.loads(tree_json_str)
        else:
            self.children = children #dict - keys: concept, values: list of immediate children of the concept
            self.all_concepts = all_concepts #list: list of all concepts, each item in the list must be hashable
            self.concept_problems = concept_problems #dict keys: concept, values: list of problems corresponding to the concept
            self.all_basic_components = all_basic_components #list: All basic components that make up each problem (if no shared components between problems, they can be the same as the list of all problems)
            self.problem_components = problem_components = problem_components #dict: keys: problem, values: list of basic the problem consists of
            self.all_descendants = {}
            self.parents = {}
            self.all_ancestors = {}
            self._calculate_all_descendants('Root')
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
        return json.dumps((
            self.children,
            self.all_descendants,
            self.parents,
            self.all_ancestors,
            self.all_concepts,
            self.concept_problems,
            self.all_basic_components,
            self.problem_components
            ))

    def save_tree(self, tree_filename):
        with open(tree_filename, "w") as text_file:
            text_file.write(self.string_tree())

    def return_parents(self): #return the parents dict (a dictionary where the keys are node names and the values are a list of the names of the immediate parents of the node)
        return self.parents

    def return_all_ancestors(self): #return the all_ancestors dict (a dictionary where the keys are node names and the values are a list of the names of all the ancestors of the node)
        return self.all_ancestors

    def return_children(self): #return the children_names dict (a dictionary where the keys are node names and the values are a list of the names of the immediate childre of the node)
        return self.children

    def return_all_descendants(self): #return the all_descendants_names dict (a dictionary where the keys are node names and the values are a list of all the descendants parents of the node)
        return self.all_descendants

    def return_all_concepts(self):
        return self.all_concepts

    def return_all_basic_components(self):
        #a method to return a list of all possible components
        return self.all_basic_components

    def return_concept_problems(self):
        #a method to return a dictionary where the keys are concept names and the values are a list of all problems corresponding to that concept
        return self.concept_problems

    def return_problem_components(self):
        #a method to return a dictionary where the keys are problems and the values are a list of all components corresponding to that problem
        return self.problem_components

    def add_edges_to_progression(self, progression_graph):
    	#Add directed edges between parents and children to a graphviz graph for visualization purporses
        for node_name, node_children in self.children.items():
            for child_name in node_children:
                progression_graph.edge(node_name, child_name, contraint = 'true')

#Tree object for sorting concepts that adds items recursively
class Build_Tree(Base_Tree):
    #a tree node, each node is the head of a subtree of its descendants
    def __init__(self, tree_filename = None, name = None, data = None, comp_func = None, children = None, children_names = None, all_descendants_names = None, parent=None, verbose = False):
        if tree_filename is not None:
            alternate_tree = pickle.load(open(tree_filename, "rb" ))
            self.name = alternate_tree.name
            self.data = alternate_tree.data
            self.parent = alternate_tree.parent
            self.children = alternate_tree.parent
            self.children_names = alternate_tree.children_names
            self.all_descendants_names = alternate_tree.all_descendants_names
            self.parents = alternate_tree.parents
            #print("Alternate tree parents:",self.parents)
            self.all_ancestors = alternate_tree.all_ancestors
            self.comp_func = alternate_tree.comp_func
            self.verbose = alternate_tree.verbose
            del alternate_tree
        else:
            self.name = name #String - name of the node
            self.data = data #Build_Tree_Data object
            self.parent = parent #Tree object - immediate parent node object
            self.children = children #Dictionary - keys are the node names and the values are an array of node objects that are the immediate children of the key node
            self.children_names = children_names #Dictionary - keys are the node names and values are an array of names of the immediate children of the key node
            self.all_descendants_names = all_descendants_names #Dictionary - keys are the node names and values are an array of names of all the descendants of the key node
            self.parents = None #Dictionary - the keys are the node names and values are an array of names of the immediate parents of the key node
            self.all_ancestors = None #Dictionary - keys are the node names and values are an array of names of all the ancestors of the key node
            self.comp_func = comp_func #Function - function for comparing the data of two concepts and determine which one is harder
            	#comp_func(A, B) Returns:
            	#1 if B is harder than A
            	#0 if neither is harder than the other
            	#-1 if A is harder than B
            self.verbose = verbose #Boolean: Whether or not to print

            if children == None:
                self.children = {}
                self.children_names = {}
                self.all_descendants_names = {}
                self.children['Root'] = []
                self.children_names['Root'] = []
                self.all_descendants_names['Root'] = set()
                for concept_name in data.all_concepts:
                    self.children[concept_name] = []
                    self.children_names[concept_name] = []
                    self.all_descendants_names[concept_name] = set()
        
        
    def _add_child(self, node):
    	#inserting a child into the subtree
        if self.verbose:
            print("entering add child")
        if not(node.name in self.all_descendants_names[self.name]) and node.name != self.name: #check it is not already a descendant of the subtree it is being inserted into
            if self.verbose:
                print('add child - self_name: ' + self.name + ' child_name: '+ node.name)
            self.children[self.name].append(node)
            self.children_names[self.name].append(node.name)
            self.all_descendants_names[self.name].add(node.name)

    def _remove_child(self, node):
    	#remove a child from the subtree
        if self.verbose:
            print('remove child - child_name: ' + node.name + ' self_name: ' + self.name)
        for index, child in enumerate(self.children[self.name]):
            if child.name == node.name:
                del self.children[self.name][index]
                del self.children_names[self.name][index]
                break
    
    def _check_tree(self, node):
        #check your sibling's children to see if they are also your children, if they are then add them to the list of your children too
        for child in self.children[self.name]:
            node.insert_node(child.name)
            child._check_tree(node)
            
    def insert_node(self, node_name):
        concept_name = node_name
        concept_trace = concept_name
        if concept_name not in self.data.data['traces']:
            self.data.data['traces'][concept_name] = concept_trace
            prim_traces = create_ngrams(concept_trace, self.data.n)
            self.data.data['traces_ngrams'][concept_name] = prim_traces
    	#insert a new node  into your subtree recursively
        if self.name != node_name:
            difficulty = self.comp_func(self.name, node_name, self.data.data)
            if self.verbose:
                print('node_name: ' + node_name + ' self_name: ' + self.name + " difficulty: " + str(difficulty))

            if difficulty == 1: #If the node is harder than you then it belongs somewhere in your subtree
                if len(self.children[self.name]) == 0:
                    #If you have no children, then the child is your child
                    if self.verbose:
                        print('no children and harder so insert')
                    node = Build_Tree(name = node_name, data = self.data, children = self.children, children_names = self.children_names, all_descendants_names = self.all_descendants_names, parent = self, comp_func = self.comp_func, verbose = self.verbose)
                    self._add_child(node)
                    
                    return 1 #return 1 for inserted

                else:
                    #If you have children, check if the node is your children's child and try to insert it into your children's subtrees
                    temp_children = list(self.children[self.name])
                    total_harder = 0
                    for child in temp_children:
                        total_harder = total_harder + child.insert_node(node_name)
                    if total_harder  == 0: # if child was not inserted, then it is your child
                        if self.verbose:
                            print('not inserted, so insert')
                        
                        node = Build_Tree(name = node_name, data = self.data, children = self.children, children_names = self.children_names, all_descendants_names = self.all_descendants_names, parent = self, comp_func = self.comp_func, verbose = self.verbose)
                        for child in temp_children:
                            child._check_tree(node)
                        self._add_child(node)
                    self.all_descendants_names[self.name].add(node_name)
                    return 1 #return 1 for inserted
                
            elif difficulty == 0: #Cannot say one is more difficult than the other
                return 0 #return 0 for not inserted

            else: #difficulty == -1, means you are harder than the node so it is your parent
                if self.verbose:
                    print('child is harder so add as parent')
                
                node = Build_Tree(name = node_name, data = self.data, children = self.children, children_names = self.children_names, all_descendants_names = self.all_descendants_names, parent = self.parent, comp_func = self.comp_func, verbose = self.verbose)

                #remove yourself from your parent
                self.parent._remove_child(self)

                #add the new node under your parent
                for child in self.children[self.parent.name]:
                    child._check_tree(node)
                self.parent._add_child(node)
                self.parent = node

                #reinsert yourself starting from your new parent 
                node.insert_node(self.name)
                return 1 #return 1 for inserted
        else:
            return 1 #1 because the node was already inserted
    
    def _add_parents(self, parents, all_ancestors):
    	#Add parents into the 
        if self.parent != None:
            parents[self.name].add(self.parent.name)
            all_ancestors[self.name].update(all_ancestors[self.parent.name])
            all_ancestors[self.name].add(self.parent.name)
                
        for child in self.children[self.name]:
            child.parents = parents
            child.all_ancestors = all_ancestors
            child._add_parents(parents, all_ancestors)

    def add_edges_to_progression(self, progression_graph):
    	#Add directed edges between parents and children to a graphviz graph for visualization purporses
        for child_name, child_children in self.children.items():
            for child in child_children:
                progression_graph.edge(child_name, child.name, contraint = 'true')
    
    def calculate_parents(self):
        #print(self.all_descendants_names)
    	#calculate the parents of the nodes
        if self.parents == None:
            parents = {}
            all_ancestors = {}
            self.parents = parents
            self.all_ancestors = all_ancestors
            parents[self.name] = set()
            all_ancestors[self.name] = set()
            for child in self.all_descendants_names[self.name]:
                parents[child] = set()
                all_ancestors[child] = set()
            self._add_parents(parents, all_ancestors)

    def return_parents(self): #return the parents dict (a dictionary where the keys are node names and the values are a list of the names of the immediate parents of the node)
        #print("Descendant Names - Build")
        if self.parents == None:
            self.calculate_parents()
        #print(self.parents)
        #print(self.parents.items())
        return {key:remove_item(items_list, 'Root') for key, items_list in self.parents.items() if key != 'Root'}

    def return_all_ancestors(self): #return the all_ancestors dict (a dictionary where the keys are node names and the values are a list of the names of all the ancestors of the node)
        if self.parents == None:
            self.calculate_parents()
        return {key:remove_item(items_list, 'Root') for key, items_list in self.all_ancestors.items() if key != 'Root'}

    def return_children(self): #return the children_names dict (a dictionary where the keys are node names and the values are a list of the names of the immediate childre of the node)
        return self.children_names

    def return_all_descendants(self): #return the all_descendants_names dict (a dictionary where the keys are node names and the values are a list of all the descendants parents of the node)
        return {key:remove_item(items_list, 'Root') for key, items_list in self.parents.items() if key != 'Root'}

    def print_tree(self, prepend_string=""):
        print(prepend_string + self.name)
        prepend_string=prepend_string+"  "
        for child in self.children[self.name]:
            child.print_tree(prepend_string = prepend_string)
        return

    def return_all_concepts(self):
        return self.data.all_concepts

    def return_all_basic_components(self):
        #a method to return a list of all possible components
        return self.data.all_basic_components

    def return_concept_problems(self):
        #a method to return a dictionary where the keys are concept names and the values are a list of all problems corresponding to that concept
        return self.data.concept_problems

    def return_problem_components(self):
        #a method to return a dictionary where the keys are problems and the values are a list of all components corresponding to that problem
        return self.data.problem_components
    
    def save_tree(self, tree_filename):
        pickle.dump(self, open(tree_filename, "wb" ))
