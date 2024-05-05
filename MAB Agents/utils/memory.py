
import math

def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)

TIME_TYPES = enum('DISCRETE', 'CONTINUOUS')
MEMORY_TYPES = enum('MCM_AVERAGE', 'MCM_LAST', 'LINEAR', 'EXPONENTIAL')
REVIEW_TYPES = enum('IN_PROGRESSION', 'AS_NECESSARY')

def memory_update(memory_type, times_list, current_time_stamp, memory_multiplier = None, base_memory = 10000):
	if memory_type == MEMORY_TYPES.MCM_AVERAGE:
		problem_memory = 0
		for idx, item_time in enumerate(times_list):
			problem_memory += (math.exp((item_time- current_time_stamp)/(float(idx+1))))/float(len(times_list))

	elif memory_type == MEMORY_TYPES.MCM_LAST:
		problem_memory = math.exp((times_list[-1]-current_time_stamp)/float(len(times_list)))

	elif memory_type == MEMORY_TYPES.LINEAR:
		if len(times_list) * memory_multiplier > current_time_stamp - times_list[-1]: #doesn't need practice
			problem_memory = 1
		else: # needs practice
			problem_memory = -1

	elif memory_type == MEMORY_TYPES.EXPONENTIAL:
		if math.exp(len(times_list)) * memory_multiplier > current_time_stamp - times_list[-1]: #doesn't need practice
			problem_memory = 1
		else: # needs practice
			problem_memory = -1
	else:
		problem_memory = base_memory

	return problem_memory

def get_memory_strengths(memory_type, problems_history, current_time_stamp, memory_multiplier = None, base_memory = 10000):
	problems_memory = {}
	for key, times_list in problems_history.items():
		if len(times_list) == 0:
			problems_memory[key] = base_memory
		else:
			problems_memory[key] = memory_update(memory_type, times_list, current_time_stamp, memory_multiplier)
	return problems_memory