# Hierarchical Multi-Armed Bandit Intelligent Tutor

We combine recent literature on multi-armed bandit (MAB) intelligent tutoring techniques into an open-sourced and simply deployable hierarchical MAB algorithm, capable of progressing students concurrently through concepts and problems, determining ideal recommended problem difficulties, and assessing latent memory decay. We evaluate our algorithm using simulated groups of 500 students, utilizing Bayesian Knowledge Tracing (BKT) to estimate students' content mastery.

Note this code was founded [on the scaffolding by Tong Mu](https://github.com/StanfordAI4HI/Automatic_Curriculum_ZPDES_Memory)

## Installation

The following packages are required:

```bash
pip install Digraph
pip install numpy
pip install matplotlib
```

## Usage

To run the joint progression algorithm, consider the following code:
```python
# import MAB
from hierarchical_progression_algorithm.Joint_Progression_Algorithm import Joint_Progression_Algorithm

# initialize MAB with a valid concept
section_name = "search"
jpa = Joint_Progression_Algorithm(section_name)

# obtain current concept name and the associated question being assessed
curConceptName, curQuestionId = jpa.getCurrentQuestionId()

# update the student's answer correctness
studentCorrectness = True
jpa.updateStudentCorrectness(studentCorrectness)
```
- ```jpa = Joint_Progression_Algorithm(concept_tree_name)``` initializes the intelligent tutor with a section name from ```./hierarchical_progression_algorithm/instructor_data/problems.json```.
- ```curConceptName, curQuestionId = jpa.getCurrentQuestionId()``` returns the current concept and question id that the student should be assessed on, calculated according to our paper's algorithm
- ```jpa.updateStudentCorrectness(studentCorrectness)``` allows the supervisor to update the algorithm with the student's correctness to the aforementioned problem given

## Customization

To modify, apply, or implement this algorithm yourself, consider the following revisions:
- ```./hierarchical_progression_algorithm/instructor_data``` contains the tree structures and problem information being tested.
  - ```concept_trees.json``` contains each section's concept tree. This must begin at the root and each concept must be included as a key with the values being a list of concepts the mastery of the key leads to.
  - ```problems.json``` is a list of the problems that each concept contains
    - Each concept name must be equal to the concept name in the ```concept_trees.json``` file (mapping in the code)
    - Each concept has a list of problems included
      - Each problem has four fields:
        - ```question``` (optional) str: the question being asked
        - ```choices``` (optional) list[str]: all possible answers the student can select
        - ```solution``` (optional) list[str]: the correct answer(s) to the problem
        - ```difficulty``` (optional) int: the difficulty of the problem between [1,5]
        - ```id``` (required) str: a *unique* id, which cannot be shared with any other problem)
- ```./hierarchical_progression_algorithm/Joint_Progression_Algorithm.py``` contains parameters used in the fine-tuning of the algorithm
  - ```params_concept``` and ```params_problem``` contain the parameters and constants used for mastery definition, window size, memory effects, and min/max concept assessments
- ```./hierarchical_progression_algorithm/mab_agents/ZPDES_Memory_PROBLEM.py``` contains parameters for the problem difficulty fine-tuning of the algorithm
  - ```DEFAULT_PARAMS``` in particular contains ```alpha1```,```alpha2```,```alpha3```,```alpha4```, and ```tau```, which may be adjusted to alter the severity of problems' difficulty on their choice by the MAB.

## Examples

- An example for running the hierarchical MAB intelligent tutor is located at ```./example/transient_question_recommendation_example.ipynb```
- An example for visualizing the trees created by the concept MAB and the problem MABs are located at ```./example/tree_visualization_example.ipynb```

## Simulation Data

Our BKT simulation data of 1500 students (groups of 500 students each) can be found at ```./simulations/sim_data```, with the data plotted at ```./simulations/mab-bkt-sim-avg-prog-autosave.pdf```. The plotting script can be found at ```./simulations/plot_simulated_data.m```.

## Citation

Castleman and Salleb-Aouissi, 2024. Coordination and Cooperation in Multi-Agent Reinforcement Learning Workshop, First Annual Conference on Reinforcement Learning. In review.

## Questions

Please contact bc3029@columbia.edu for any questions or comments.
