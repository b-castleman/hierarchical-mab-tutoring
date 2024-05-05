import json
import time
import random
import copy
import memory
import math
import numpy as np

current_time = lambda: int(round(time.time() * 100))

DEFAULT_PARAMS = {
            #Must be defined
            'history_length': 2,
            'progress_threshold': 0.49,
            'memory_threshold': math.exp(-18),
            'memory_multiplier': 1000000,
            
            #Optional
            'min_concept_attempts': 2, #defaults to history_length
            'max_concept_attempts': math.inf, #some really large value
            'min_weight': 0.001, #some really small non-zero value for purposes of avoiding dividing by zero
            'gamma': 0.1, #Default
            'initial_weight': 0.5, #Default
            'initial_weight_multiplier': 4, #Default

            # Difficulty parameters
            'alpha1': 1.3,
            'alpha2': 1.0,
            'alpha3': 1.0/1.3, # set as the inverse
            'alpha4': 1.0/1.0, # set as the inverse
            'tau': 7.37, # difficulty damper
            }

class ZPDES_Memory_PROBLEM(object):

    def __init__(self, progression_tree, params = DEFAULT_PARAMS, problem_difficulties=None):

        # Get problem difficulties
        self.problem_difficulties = problem_difficulties
        
        #Load in the tree
        self.progression_tree = progression_tree
        all_concepts_list = self.progression_tree.return_all_concepts()
        # print("ALL CONCEPTS:",all_concepts_list)
        all_components_list = self.progression_tree.return_all_basic_components()

        for concept in all_concepts_list:
            assert concept in problem_difficulties.keys(), "concept does not have defined difficulty"

        assert len(self.problem_difficulties) == len(all_concepts_list), "problem difficulty size != concept list size"
        
        #ZPDES parameters
        self.params = params
        #check params are there:
        assert 'history_length' in params, "history_length is not defined"
        assert 'progress_threshold' in params, "progress_threshold is not defined"
        assert 'memory_threshold' in params, "memory_threshold is not defined"
        assert 'memory_multiplier' in params, "memory_multiplier is not defined"

        assert params['history_length'] % 2 == 0, "history length is not even"

        if 'min_concept_attempts' not in self.params:
        	self.params['min_concept_attempts'] = self.params['history_length']
        if 'max_concept_attempts' not in self.params:
        	self.params['max_concept_attempts'] = DEFAULT_PARAMS['max_concept_attempts']
        if 'min_weight' not in self.params:
        	self.params['min_weight'] = DEFAULT_PARAMS['min_weight']
        if 'gamma' not in self.params:
        	self.params['gamma'] = DEFAULT_PARAMS['gamma']
        if 'initial_weight' not in self.params:
        	self.params['initial_weight'] = DEFAULT_PARAMS['initial_weight']
        if 'initial_weight_multiplier' not in self.params:
        	self.params['initial_weight_multiplier'] = DEFAULT_PARAMS['initial_weight_multiplier']
            
        if 'alpha1' not in self.params:
        	self.params['alpha1'] = DEFAULT_PARAMS['alpha1']
        if 'alpha2' not in self.params:
        	self.params['alpha2'] = DEFAULT_PARAMS['alpha2']
        if 'alpha3' not in self.params:
        	self.params['alpha3'] = DEFAULT_PARAMS['alpha3']
        if 'alpha4' not in self.params:
        	self.params['alpha4'] = DEFAULT_PARAMS['alpha4']
        if 'tau' not in self.params:
        	self.params['tau'] = DEFAULT_PARAMS['tau']

        self.concept_problems = self.progression_tree.return_concept_problems()
        self.problem_components = self.progression_tree.return_problem_components()

        self.all_prereqs = self.progression_tree.return_all_ancestors()
        self.prereqs = self.progression_tree.return_parents()
        #print("Self prereqs:",self.prereqs)
        self.children = self.progression_tree.return_children()
        
        self.weights = {node:self.params['initial_weight'] for node in all_concepts_list}
        self.weights_histories = {node:[self.params['initial_weight'], self.params['initial_weight']] for node in all_concepts_list}
        self.correctnesses = {node:[] for node in all_concepts_list}
        self.mastered_concepts = [] #which concepts are mastered
        
        self.ZPD = [node for node in all_concepts_list if len(self.prereqs[node]) == 0]
        random.shuffle(self.ZPD)
        self.length_ZPD = len(self.ZPD)

        self.concept = None
        self.problem = None
        self.attempts = 0
        self.last_problem = None
        self.last_concept = None
        
        #Memory Variables
        self.memory_concept = None

        #set the next three variables to None if want to turn off memory
        self.memory_type = memory.MEMORY_TYPES.MCM_AVERAGE
        self.time_type = memory.TIME_TYPES.DISCRETE
        self.review_type = memory.REVIEW_TYPES.AS_NECESSARY
        #self.memory_type = None
        #self.time_type = None
        #self.review_type = None
        
        self.begin_continuous_time = current_time()
        self.discrete_time = 0

        self.concepts_seen_history = {node:[] for node in all_concepts_list}
        self.concepts_memory = {node:10000 for node in all_concepts_list}
        self.components_seen_history = {component:[] for component in all_components_list}
        self.components_memory = {component:0.0001 for component in all_components_list}
        
        #Data Variables:
        self.problems_history = []
        self.answers_history = []

        # Initialize Difficulty Multiplier
        self.m = dict()
        for concept in all_concepts_list:
            self.m[concept] = math.exp(-(float(self.problem_difficulties[concept] - 3.0)**2/self.params['tau']))

        
        #Get a new problem
        self.new_problem()


    def get_current_time(self):
        return current_time() - self.begin_time

    def new_problem(self):
        
        self.attempts = 0
        if self.length_ZPD == 0:
            self.memory_concept = None
            self.problem = None
            self.concept = None
        else:
    		#CHOOSE CONCEPT
            self.calculate_concepts_memory()
            if self.memory_concept == None:

                # Remove repeat possibilities so we dont get the same problem twice
                # print("self.ZPD:")
                # print(self.ZPD)
                ZPD = copy.deepcopy(self.ZPD)
                
                # print("Last Concept:")
                # print(self.last_concept)
                if len(ZPD) > 1 and self.last_concept in ZPD:
                    ZPD.remove(self.last_concept)
                    # idx = ZPD.index(self.last_concept)
                    # del ZPD[idx]
                    # del 
                # print("ZPD:")
                # print(ZPD)

                length_ZPD = len(ZPD)
                weights_ZPD = np.zeros(length_ZPD)
                zeta = np.ones(length_ZPD) / float(length_ZPD)
                gamma = self.params['gamma']
                

                weights_sum = 0
                for idx, concept in enumerate(ZPD):
                    if len(self.weights_histories[concept]) > 2:
                        mean_weight = np.mean(self.weights_histories[concept][1:])
                    else:
                        mean_weight = np.mean(self.weights_histories[concept])
                    self.weights[concept] = max(mean_weight, self.params['min_weight'])
                    weights_ZPD[idx] = self.weights[concept]
                    # print("Before for",concept,":",weights_ZPD[idx])
                    weights_ZPD[idx] *= self.m[concept] # difficulty alter multiplier
                    # print("After for",concept,":",weights_ZPD[idx])
                    
                    weights_sum += weights_ZPD[idx]
                    

                print("Pre Explore Problem Weights:")
                print(weights_ZPD)
                
                #add exploration in
                #weights_ZPD = weights_ZPD + (float(weights_sum) * gamma/( 1.0 - gamma )) * zeta
                weights_ZPD = weights_ZPD * (1-gamma) + gamma/length_ZPD # (float(weights_sum) * gamma/( 1.0 - gamma )) * zeta 
                #weights_sum += weights_sum * gamma/float( 1.0 - gamma)
                weights_sum = sum(weights_ZPD)
                concepts_selection = copy.deepcopy(ZPD)

                print("Problem ZPD:")
                print(concepts_selection)
                print("Post Explore Problem Weights:")
                print(weights_ZPD)
                

                

                #if we are accounting for memory by adding it into the concepts ZPDES should select from
                if self.review_type == memory.REVIEW_TYPES.IN_PROGRESSION:
                    print("REVIEW TYPES IN PROGRESSION")
                    memory_threshold = self.params['memory_threshold']
                    memory_multiplier = self.params['memory_multiplier']

                    weights_memory = np.zeros(len(self.mastered_concepts))
                    for idx, item in enumerate(self.mastered_concepts):
                        weights_memory[idx] = memory_multiplier * max(memory_threshold - self.concepts_memory[item], 0)
                        weights_sum += weights_memory[idx]

                    weights_ZPD = np.hstack([weights_ZPD, weights_memory])
                    concepts_selection = list(concepts_selection) + self.mastered_concepts

                #select concept
                pa = weights_ZPD / float(weights_sum)
                print("Problem Probability")
                print(pa)
                # print("Probabilities - pa")
                # print(pa)
                # print("Concept Selection")
                # print(concepts_selection)
                self.concept = np.random.choice(concepts_selection, 1, p=pa)[0]

            if self.review_type == memory.REVIEW_TYPES.AS_NECESSARY:
                memory_threshold = self.params['memory_threshold']
                self.memory_concept = None
                for key in self.prereqs[self.concept]:
                    if (self.concepts_memory[key] < memory_threshold) and (key not in self.ZPD):
                        self.memory_concept = key
                        break
            
            #SET PROBLEM
            self.set_problem()
        
    def set_problem(self):
        concept = self.memory_concept
        if concept == None:
            concept = self.concept

        concept_problems = copy.deepcopy(self.concept_problems[concept])
        if len(concept_problems) > 1 and self.last_problem in concept_problems:
            concept_problems.remove(self.last_problem)
        problem_scores = np.zeros(len(concept_problems))
        for idx, problem in enumerate(concept_problems):
            problem_components = self.problem_components[problem]
            for component in problem_components:
                problem_scores[idx] += 1.0/self.components_memory[component]

        max_problem_arg = np.argmax(problem_scores)
        self.problem = concept_problems[max_problem_arg]


    def student_attempt_update(self, student_attempt_correctness):
        
        if student_attempt_correctness:
            self.student_answer_update(self.attempts == 0)
        else:
            self.discrete_time += 1
            self.attempts += 1
            
    def student_answer_update(self, student_answer_correctness):
        self.discrete_time += 1
        if not student_answer_correctness:
            self.attempts = max(1, self.attempts)
        self.answers_history.append(self.attempts)
        self.problems_history.append(self.problem)
        self.last_problem = self.problem
        self.last_concept = self.concept

        #if not self.learning_mode and student_answer_correctness:
        if student_answer_correctness:
            self.update_memories()

        if self.memory_concept is None and self.concept in self.ZPD: #If not reviewing
            history_length = self.params['history_length']
            min_concept_attempts = self.params['min_concept_attempts']
            progress_threshold = self.params['progress_threshold']
            max_concept_attempts = self.params['max_concept_attempts']
            concept = self.concept

            alpha1 = self.params['alpha1']
            alpha2 = self.params['alpha2']
            alpha3 = self.params['alpha3']
            alpha4 = self.params['alpha4']

            self.correctnesses[concept].append(student_answer_correctness)
            #print("CORRECTNESS MAP:")
            #print(self.correctnesses)
            num_concept_attempts = len(self.correctnesses[concept])

            # Not enough concept attempts, it'll go out of bounds. Let's assume a bunch of incorrect concept attempts instead
            positiveRewardEnd = len(self.correctnesses[concept])
            positiveRewardStart = max(0,positiveRewardEnd - int(history_length/2))

            negativeRewardEnd = positiveRewardStart
            negativeRewardStart = max(0,negativeRewardEnd - int(history_length/2))

            #print(positiveRewardStart,":",positiveRewardEnd,"--",negativeRewardStart,":",negativeRewardEnd)

            # Add positive reward first
            reward = sum(self.correctnesses[concept][positiveRewardStart:positiveRewardEnd]) / float(positiveRewardEnd-positiveRewardStart)

            # Add negative reward last (if there is any yet, otherwise assume previously incorrect)
            reward += -sum(self.correctnesses[concept][negativeRewardStart:negativeRewardEnd]) / float(history_length) if negativeRewardEnd-negativeRewardStart > 0 else 0
                
                
            #print("Reward:")
            #print(reward)
            self.weights_histories[concept].append(reward)

            # For the problem MAB, we'll automatically remove this problem from the ZPD if answered correctly
            if student_answer_correctness or (len(self.correctnesses[concept]) >= min_concept_attempts and sum(self.correctnesses[concept][negativeRewardStart:]) / float(self.params['history_length']) >= progress_threshold) or (len(self.correctnesses[concept]) >= max_concept_attempts):
                self.ZPD.remove(concept)
                self.mastered_concepts.append(concept)

                initial_weight = self.params['initial_weight']*self.params['initial_weight_multiplier']
                for child in self.children[concept]:
                    can_add = True
                    for prereq in self.prereqs[child]:
                        if prereq not in self.mastered_concepts:
                            can_add = False

                    if can_add:
                        self.ZPD.append(child)
                        self.weights_histories[child][0] = initial_weight

            self.length_ZPD = len(self.ZPD)


            
            ## Correct weights based on difficulties and answer correctness

            # print("Before:")
            # print(self.weights_histories)

            # print("Gamma_b",self.params['gamma'])
            
            # Get question difficulty
            qs_difficulty = self.problem_difficulties[concept]
            if student_answer_correctness:
                # Increase weights for questions more difficult than the last question
                for zpdConcept in self.ZPD:
                    if self.problem_difficulties[zpdConcept] > qs_difficulty:
                        self.m[zpdConcept] *= alpha1 # alpha1 > 1
                    elif self.problem_difficulties[zpdConcept] < qs_difficulty:
                        self.m[zpdConcept] *= alpha3 # alpha3 = 1/alpha1
                        
                # Increase exploration factor
                self.params['gamma'] *= alpha2
            else:
                # Decrease weights for questions more difficult than the last question
                for zpdConcept in self.ZPD:
                    if self.problem_difficulties[zpdConcept] > qs_difficulty:
                        self.m[zpdConcept] *= alpha3
                    elif self.problem_difficulties[zpdConcept] > qs_difficulty:
                        self.m[zpdConcept] *= alpha1

                # Decrease exploration factor
                self.params['gamma'] *= alpha4

            # print("After:")
            # print(self.weights_histories)
            # print("Gamma_a",self.params['gamma'])
                

        self.new_problem()

    def update_memories(self):
        if self.time_type == memory.TIME_TYPES.CONTINUOUS:
            current_time_stamp = self.get_current_time()
        else:
            current_time_stamp = self.discrete_time

        concept_key = self.memory_concept
        if concept_key == None:
            concept_key = self.concept

        #add time reviewed in current_time_stamp and those of concepts easier than it
        self.concepts_seen_history[concept_key].append(current_time_stamp)
        for key in self.all_prereqs[concept_key]:
            self.concepts_seen_history[key].append(current_time_stamp)
        
        #add time reviewed for the problem components
        problem_components = self.problem_components[self.problem]
        for problem_component in problem_components:
            self.components_seen_history[problem_component].append(current_time_stamp)

    def calculate_concepts_memory(self):
        if self.time_type == memory.TIME_TYPES.CONTINUOUS:
            current_time_stamp = self.get_current_time()
        else:
            current_time_stamp = self.discrete_time

        self.concepts_memory = memory.get_memory_strengths(self.memory_type, self.concepts_seen_history, current_time_stamp, memory_multiplier = self.params['memory_multiplier'], base_memory = 10000)
        self.components_memory = memory.get_memory_strengths(self.memory_type, self.components_seen_history, current_time_stamp, memory_multiplier = self.params['memory_multiplier'], base_memory = 0.0001)
    
    def get_current_problem(self):
        return self.problem
            
    def get_progression_student_info(self):
        return (self.problems_history, self.answers_history)