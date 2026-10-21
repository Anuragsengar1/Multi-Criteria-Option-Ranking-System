# Multi-Criteria-Option-Ranking-System
Short Theory of the Project

This project is a Decision Support System that helps users compare different options and choose the best one using a Weighted Decision Matrix.

Main Idea

The user:

Defines criteria (Price, Battery, Speed, etc.).
Assigns importance weights to each criterion.
Enters scores for different options.
The program calculates weighted scores and ranks the options.
How It Works

1. Validation

validate_criteria() checks if criteria and weights are valid.
validate_options() checks if every option has scores for all criteria.

2. Weight Normalization

normalise_weights() converts weights into percentages that add up to 1.
Example:
Price = 8
Battery = 4
Total = 12
Normalized weights:
Price = 8/12 = 0.67
Battery = 4/12 = 0.33

3. Score Normalization

normalise_scores() scales all scores between 0 and 1.
For Benefit criteria: higher values are better.
For Cost criteria: lower values are better.

4. Weighted Score Calculation

weighted_totals() multiplies normalized scores by normalized weights.
The total score determines the overall performance of an option.

5. Ranking

rank() sorts options from highest score to lowest score.

6. Scenario Analysis

scenario_comparison() tests different situations such as:
Budget First
Performance First
Portability First

7. Sensitivity Analysis

one_at_a_time() changes weights by ±50%.
Checks whether the winning option changes.
Helps determine if the decision is robust.

8. Explanation Generation

explain() generates a human-readable summary explaining:
The winner
Score difference
Biggest strength
Weakest area

9. User Input

collect_inputs() allows users to enter their own criteria and options.

10. Demo Mode

demo() provides a sample laptop comparison with predefined data.
Objective

The objective of this project is to assist users in making objective and data-driven decisions by evaluating multiple alternatives based on weighted criteria, ranking the options, and analyzing the robustness of the final decision through scenario and sensitivity analysis.

This is a good Python mini-project because it demonstrates:

Functions
Dictionaries
Loops
Input Validation
Data Analysis
Decision-Making Algorithms
Real-world Problem Solving
Provide your feedback on BizChat
FilesFiles
