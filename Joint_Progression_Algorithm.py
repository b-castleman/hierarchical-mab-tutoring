import copy
from tree import Static_Tree, Build_Tree_Data
import pickle
import math
import random
from ZPDES_Memory_CONCEPT import ZPDES_Memory_CONCEPT
from ZPDES_Memory_PROBLEM import ZPDES_Memory_PROBLEM
import numpy as np
import collections
from graphviz import Digraph
import sys
from compare_functions import compare_ngrams
import re
import os
import json

class Joint_Progression_Algorithm(object):

    def __init__(self, curSection, problemsFilePath = './problems/problems.json'):

        self.problemsFilePath = problemsFilePath

        self.progression_tree_concept = self.makeConceptProgressionTree(curSection)
        self.progression_tree_problem_dict, self.problemDifficulties = self.makeProblemProgressionTrees()
    
    
        params_concept = {
            'history_length': 4,
            'progress_threshold': 0.74,
            'memory_threshold': math.exp(-12),
            'memory_multiplier': 10e10,
            'max_concept_attempts': 10,
            'min_concept_attempts': 2,
        }
    
        self.progression_algorithm_concept = ZPDES_Memory_CONCEPT(self.progression_tree_concept, params = params_concept)
    
        params_problem = {
            'history_length': 2,
            'progress_threshold': 0.74,
            'memory_threshold': math.exp(-12),
            'memory_multiplier': 10e10,
            'max_concept_attempts': 8,
            'min_concept_attempts': 1,
        }
    
        
        self.progression_algorithm_problem_dict = dict()
        
        all_concepts = self.progression_tree_concept.return_all_concepts()
        for concept in all_concepts:
            progression_tree_problem = self.progression_tree_problem_dict[concept]
    
            cur_concept_problem_difficulties = dict()
    
            all_problems = progression_tree_problem.return_all_concepts()

            for problem in all_problems:
                cur_concept_problem_difficulties[problem] = self.problemDifficulties[problem]
    

            self.progression_algorithm_problem_dict[concept] = ZPDES_Memory_PROBLEM(progression_tree_problem, params = params_problem, problem_difficulties = cur_concept_problem_difficulties)

            

    def getCurrentQuestionId(self):
        # get next question

        concept_give = self.progression_algorithm_concept.get_current_problem()
        self.curConcept = concept_give

        if self.curConcept is None: # Done with the concept algorithm!
            return None, None

        problem_give = self.progression_algorithm_problem_dict[concept_give].get_current_problem()
        self.curProblem = problem_give
        self.current_progression_algorithm_problem = self.progression_algorithm_problem_dict[concept_give]

        # No more problems in this concept yet we're still being asked it
        if self.curProblem is None: 
            # We need to remove this concept from the concept MAB, there's nothing else to ask
            self.progression_algorithm_concept.ZPD.remove(self.curConcept)
            self.progression_algorithm_concept.mastered_concepts.append(self.curConcept)

            initial_weight = self.progression_algorithm_concept.params['initial_weight']*self.progression_algorithm_concept.params['initial_weight_multiplier']
            for child in self.progression_algorithm_concept.children[self.curConcept]:
                can_add = True
                for prereq in self.progression_algorithm_concept.prereqs[child]:
                    if prereq not in self.progression_algorithm_concept.mastered_concepts:
                        can_add = False

                if can_add:
                    self.progression_algorithm_concept.ZPD.append(child)
                    self.progression_algorithm_concept.weights_histories[child][0] = initial_weight

            self.progression_algorithm_concept.length_ZPD = len(self.progression_algorithm_concept.ZPD)

            # Update the concept MAB for the next problem
            self.progression_algorithm_concept.new_problem()
            
            return self.getCurrentQuestionId()

        # All is good to return!
        return self.curConcept, self.curProblem
        

    def updateStudentCorrectness(self,student_answer_correctness):
        # update student correctness

        self.progression_algorithm_concept.student_answer_update(student_answer_correctness, difficulty=self.problemDifficulties[self.curProblem])
        
        self.current_progression_algorithm_problem.student_answer_update(student_answer_correctness)


    def makeStaticTree(self,all_concepts,tree_structure):
        concept_problems = dict()
        for concept in all_concepts:
            concept_problems[concept] = [concept]
        
        
        problem_components = {}
        for concept, concept_problems_list in concept_problems.items():
            for problem in concept_problems_list:
                problem_components[problem] = [problem]
        all_basic_components = list(problem_components.keys())


        data = Build_Tree_Data(all_concepts= all_concepts, concept_problems = concept_problems, 
                       all_basic_components = all_basic_components, problem_components = problem_components, n = 1)


        return Static_Tree(children = tree_structure, all_concepts = all_concepts, 
                              concept_problems = concept_problems, all_basic_components = all_basic_components, 
                              problem_components = problem_components)
    
    def makeProblemProgressionTrees(self):

        progression_tree_problem_dict = dict()
        problem_difficulties = dict()

        all_concepts = self.progression_tree_concept.return_all_concepts()

        with open(self.problemsFilePath) as json_file:
              problemsDict = json.load(json_file)
        

        for concept in all_concepts:
            problemList = problemsDict[concept]
            

            # Define tree necessities
            all_problems = []
            tree_structure = {'Root': []}

            for problem in problemList:
                id = problem['id']
                difficulty = problem['difficulty']
                
                problem_difficulties[id] = difficulty
                
                all_problems.append(id)
                tree_structure['Root'].append(id)
                tree_structure[id] = []

            curProblemProgressionTree = self.makeStaticTree(all_problems,tree_structure)
            progression_tree_problem_dict[concept] = curProblemProgressionTree


        return progression_tree_problem_dict, problem_difficulties


    

            
            
        

        

    def makeConceptProgressionTree(self,section):
        all_concepts = []
        if section == 'ai_intro_and_defs':
            all_concepts.extend(['ai_definitions','four_schools_of_thought'])
            
            tree_structure = {
                'Root': ['ai_definitions'],
                'ai_definitions': ['four_schools_of_thought'],
                'four_schools_of_thought': []
            }
            
        elif section == 'turing_test':
            all_concepts.extend(['turing_test_definition','turing_test_examples'])
        
            tree_structure = {
                    'Root': ['turing_test_definition'],
                    'turing_test_definition': ['turing_test_examples'],
                    'turing_test_examples': []
            }
        
        elif section == 'applications_of_ai':
            all_concepts.extend(['applications_of_ai_examples'])
        
            tree_structure = {
                    'Root': ['applications_of_ai_examples'],
                    'applications_of_ai_examples': []
            }
        elif section == 'history_of_ai':
            all_concepts.extend(['gestation_and_early_enthusiasm_era','knowledge_based_era','ai_becomes_scientific'])
        
            tree_structure = {
                        'Root': ['gestation_and_early_enthusiasm_era'],
                        'gestation_and_early_enthusiasm_era': ['knowledge_based_era'],
                        'knowledge_based_era': ['ai_becomes_scientific'],
                        'ai_becomes_scientific': []
                }
        elif section == 'logical_agents':
            all_concepts.extend(['wumpus_specific','logic_review'])
        
            tree_structure = {
                        'Root': ['wumpus_specific','logic_review'],
                        'logic_review': [],
                        'wumpus_specific': [],
                }
        elif section == 'rational_agents':
            all_concepts.extend(['acting_rationally','peas','environment_types'])
        
            tree_structure = {
                'Root': ['acting_rationally'],
                'acting_rationally': ['peas', 'environment_types'],
                'peas': [],
                'environment_types': [],
            }
        elif section == 'search':
            all_concepts.extend(['search_definition','simple_search','constraint_search','adversarial_search','delete_later_sub'])
        
            tree_structure = {
                'Root': ['search_definition'],
                'search_definition': ['simple_search','constraint_search','adversarial_search'],
                'adversarial_search': ['delete_later_sub'],
                'simple_search':['delete_later_sub'],
                'constraint_search': ['delete_later_sub'],
                'delete_later_sub': []
            }
        elif section == 'ml_intro':
            all_concepts.extend(['ml_basic_concepts'])
            tree_structure = {
                'Root': ['ml_basic_concepts'],
                'ml_basic_concepts': []
            }
        elif section == 'perceptron':
            all_concepts.extend(['perceptron_qs'])
            tree_structure = {
                'Root': ['perceptron_qs'],
                'perceptron_qs': []
            }
        else:
            raise Exception('Invalid section')

        return self.makeStaticTree(all_concepts,tree_structure)

        

        
        
    
