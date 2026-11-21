AI-Based University Timetable Generator

1. Project Overview

The AI-Based University Timetable Generator is a Python-based application that automatically generates university class timetables using Artificial Intelligence techniques.

Creating university timetables manually can be challenging because multiple constraints must be considered simultaneously. These include teacher availability, classroom availability, room capacity, section schedules, and time-slot conflicts.

This project addresses the problem using a Constraint Satisfaction Problem (CSP) approach. It applies AI search techniques to find a valid timetable while satisfying the defined scheduling constraints.

The project implements and compares three techniques:

Backtracking Search: Explores possible timetable assignments and backtracks when a constraint is violated.

Minimum Remaining Values (MRV): Selects the most constrained meeting first to improve the search process.

Forward Checking: Eliminates invalid future assignments after each decision to reduce unnecessary searching.

The application provides a command-line interface (CLI) through which users can generate and view university timetables.

2. Project Objectives

Automatically generate valid university timetables.

Prevent teacher, classroom, and section scheduling conflicts.

Ensure classrooms satisfy capacity and room-type requirements.

Consider teacher availability during scheduling.

Implement and compare different AI search techniques.

Reduce unnecessary search using MRV and Forward Checking.

3. Technologies Used
  Python 3
onstraint Satisfaction Problems (CSP)
Problem formulation
Backtracking Search
MRV Heuristic
Variable selection
Forward Checking
JSON
CSV
4. AI Techniques

Backtracking Search

The algorithm assigns time slots and classrooms to meetings one at a time. If an assignment violates a constraint or leads to an impossible situation, it backtracks and tries another assignment.

Minimum Remaining Values (MRV)

MRV selects the meeting with the smallest number of remaining valid assignments. This helps the solver handle the most restricted scheduling decisions first.

Forward Checking

Forward Checking updates the available domains of unassigned meetings after every assignment. Invalid possibilities are removed, allowing the algorithm to identify conflicts earlier.

5. Expected Output

The application generates a university timetable containing the scheduled meetings, their assigned time slots, classrooms, and relevant scheduling information.

The generated timetable is checked against the defined constraints to ensure that no hard scheduling conflicts remain.

6. Project Scope

This project is designed as an educational AI application demonstrating how Constraint Satisfaction Problems and search algorithms can solve real-world scheduling problems.

It can serve as a foundation for more advanced university scheduling systems with graphical interfaces, larger datasets, and additional scheduling constraints
