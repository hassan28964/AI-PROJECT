---
geometry: margin=0.78in
fontsize: 10pt
toc-depth: 1
header-includes:
  - \usepackage{float}
  - \floatplacement{figure}{H}
colorlinks: true
linkcolor: blue
urlcolor: blue
---

```{=latex}
\begin{titlepage}
\thispagestyle{empty}
\centering
\vspace*{1.0cm}
{\Large FAST - NATIONAL UNIVERSITY OF COMPUTER AND EMERGING SCIENCES\\[0.2cm]}
{\large FAST School of Computing\\Department of Artificial Intelligence and Data Science\\Karachi Campus\\[1.0cm]}
{\large AL-2002 - Artificial Intelligence (Laboratory)\\Fall 2026\\[1.2cm]}
{\Huge\bfseries AI-Based University\\[0.15cm] Timetable Generator\\[0.8cm]}
{\Large Project Report\\[1.8cm]}
\begin{tabular}{rl}
\textbf{Prepared by:} & Student Name: \underline{\hspace{5cm}} \\
\textbf{Student ID:} & \underline{\hspace{5cm}} \\\
\textbf{Project type:} & Individual implementation \\
\textbf{Report date:} & 21 November 2026 \\
\end{tabular}
\vfill
{\large Karachi, Pakistan}
\end{titlepage}
```

\begingroup
\footnotesize
\setlength{\parskip}{0pt}
\tableofcontents
\endgroup
\newpage

# Abstract

The AI-Based University Timetable Generator is a small command-line application that creates a weekly university timetable using a Constraint Satisfaction Problem (CSP) approach. The scheduling problem is represented through variables, domains, and constraints. Each required course meeting is treated as a variable, while its domain contains feasible combinations of a weekly time slot and a suitable room. The system checks teacher availability, room availability, room type, room capacity, teacher clashes, room clashes, and student-section clashes.

Two search strategies are implemented in Python: basic backtracking and backtracking enhanced with the Minimum Remaining Values (MRV) heuristic and forward checking. The program loads a locally stored JSON dataset, creates class meetings, builds domains, searches for a complete assignment, validates the resulting timetable, displays it in the command line, and exports results to CSV. It also runs 20 repeated trials with shuffled meeting and value orders and produces charts comparing search nodes, runtime, and success rate.

The included sample contains five courses, three student sections, five teachers, four rooms, 20 weekly time slots, and 15 required class meetings. In the recorded run, both algorithms found valid schedules in all 20 trials. MRV with forward checking used fewer search nodes on average, but took longer on this small dataset because maintaining and filtering domains adds overhead. The project demonstrates how CSP search and heuristics can be applied to a practical university scheduling problem.

# 1. Introduction

## 1.1 Background

Preparing a university timetable requires several decisions to be made together. Each class meeting needs an appropriate time and room, and it must be assigned to the teacher responsible for the course. These decisions are connected: assigning one meeting may prevent another meeting from using the same time, room, teacher, or student section.

Manual scheduling using spreadsheets can require repeated checking and revision. A timetable may appear valid at first but later create a conflict when another course is added. An automated scheduler can represent these rules explicitly and search for a complete assignment that satisfies them.

## 1.2 Problem statement

The project addresses the problem of assigning every required course-section meeting to a feasible weekly time slot and classroom while satisfying the scheduling rules. The core hard constraints are:

1. A teacher cannot teach two meetings in the same time slot.
2. A classroom cannot host two meetings in the same time slot.
3. Students in the same section cannot be assigned two meetings in the same time slot.
4. A room must have the required room type and sufficient capacity.
5. The teacher and room must be available in the selected time slot.
6. The required number of weekly meetings must be generated for each course and section.

## 1.3 Motivation

The project was selected because university timetabling is a recognizable scheduling problem with many interacting restrictions. It provides a practical setting in which to demonstrate CSP modelling, recursive search, heuristic variable selection, domain pruning, and algorithm evaluation.

# 2. Project Objectives

The objectives of the implementation are:

- Represent university timetabling as a Constraint Satisfaction Problem.
- Read course, teacher, room, and time-slot information from a local JSON file.
- Generate one scheduling variable for every required course-section meeting.
- Build feasible time-slot and room domains for those variables.
- Prevent teacher, room, and section clashes.
- Implement plain backtracking as a baseline search algorithm.
- Implement MRV and forward checking to guide and prune the search.
- Independently validate the generated timetable.
- Display the schedule and export the timetable and experiment data as CSV files.
- Compare the two algorithms using search nodes, backtracks, runtime, and success rate.

# 3. Scope and Assumptions

## 3.1 Included in the current implementation

The current version is a local, single-user command-line program. It uses a JSON input file and supports a maximum of five courses and five distinct student sections. It includes two CSP solvers, a final timetable validator, CSV exports, and three experiment charts.

The sample dataset is synthetic and is stored locally. No external dataset, API key, university database, or network connection is required.

## 3.2 Outside the current scope

The implementation does not include a graphical user interface, user accounts, a database server, live integration with university systems, automatic student enrolment, multi-campus scheduling, or machine-learning-based prediction. It does not optimize soft preferences such as teacher preferred days, balanced daily workloads, or minimizing gaps between classes. These items may be considered in future versions.

## 3.3 Important modelling assumptions

- Each time slot is a discrete unit identified by a unique slot ID.
- Different slot IDs are treated as different, non-conflicting periods. The current conflict checker does not compare arbitrary clock-time interval overlaps.
- If teacher or room `available_slots` is not provided in the JSON file, that resource is treated as available in every defined time slot.
- Room type must match the course's required room type exactly.
- The student count and room requirement are defined on each course record and are applied to each of its sections.

# 4. AI Problem Formulation

## 4.1 Constraint Satisfaction Problem

A CSP consists of variables, domains, and constraints. The project maps the timetable problem to these components as follows.

| CSP component | Project representation |
|---|---|
| Variables | Individual course-section class meetings |
| Domains | Feasible time-slot and room combinations for each meeting |
| Constraints | Teacher, room, section, availability, room-type, and capacity rules |
| Initial state | All meetings are unassigned; each begins with its generated domain |
| Goal state | Every required meeting is assigned and all hard constraints are satisfied |

A scheduling assignment for one meeting can be represented as:

`(slot_id, day, start, end, room_id, room_name)`

For example, assigning an Artificial Intelligence meeting to Monday 09:00-10:30 in Computer Lab 201 is one domain value for that meeting.

## 4.2 Variables

A variable represents one occurrence of a course for one student section. The program generates these variables from the course's section list and `sessions_per_week` value.

For a course with three sections and one session per week, the program creates three meetings. In the sample dataset, five courses each serve three sections and require one weekly meeting per section:

\[
5 \text{ courses} \times 3 \text{ sections} \times 1 \text{ meeting} = 15 \text{ variables}
\]

Meeting IDs follow a pattern such as `AI_BCY-3A_1`, where the values identify the course, section, and session number.

## 4.3 Domains

A domain is the list of possible values for a meeting. Each value combines one time slot and one room. A value is included only when:

- the teacher is available in that slot;
- the room is available in that slot;
- the room type matches the course requirement; and
- the room capacity is at least the course's student count.

For the included sample, there are 20 time slots and two suitable rooms for each course room type. Because availability lists are omitted, all teachers and rooms default to being available in every slot. Each sample meeting therefore starts with up to 40 candidate time-room values before conflicts with other assigned meetings are considered.

## 4.4 Hard constraints

The implementation uses the following rules:

**Teacher clash:** If two meetings use the same time-slot ID, they cannot have the same teacher.

**Room clash:** If two meetings use the same time-slot ID, they cannot use the same room.

**Section clash:** If two meetings use the same time-slot ID, they cannot belong to the same student section.

Room type, capacity, teacher availability, and room availability are checked while the initial domains are built. The three clash constraints are checked against the current partial assignment during search.

## 4.5 PEAS description

| PEAS element | Description |
|---|---|
| Performance measure | Complete valid timetable; zero hard-constraint violations; fewer search nodes and backtracks; reasonable runtime |
| Environment | Simulated university courses, meetings, teachers, rooms, sections, and weekly time slots |
| Actuators | Assign a meeting to a time-slot and room; revise assignments through backtracking; print and export results |
| Sensors | Read input data, inspect partial assignments and domains, and check scheduling constraints |

## 4.6 Environment and agent characteristics

The proposal models this task as a fully observable, deterministic, static, discrete, single-agent environment. The implemented program works with a fixed local dataset during each run. It follows a model-based and goal-based approach: it maintains the scheduling state, checks the rules, and searches for a state in which all required meetings have been assigned validly.

# 5. System Design and Implementation

## 5.1 Program structure

To keep the project understandable for an individual developer, the implementation is organized in one Python file, `main.py`, supported by a separate `university_data.json` file. The code uses four simple classes and ordinary functions rather than a large multi-module architecture.

| Class | Responsibility |
|---|---|
| `Course` | Stores course ID, name, teacher, sections, student count, room type, and weekly sessions |
| `Teacher` | Stores teacher ID, name, and available time slots |
| `Room` | Stores room ID, name, capacity, room type, and available time slots |
| `Meeting` | Represents one required occurrence of a course for one student section |

The main functions are:

| Function | Responsibility |
|---|---|
| `load_data()` | Reads JSON, checks project limits, creates objects, and generates meetings |
| `create_domains()` | Creates feasible time-slot and room values for each meeting |
| `is_valid()` | Checks teacher, room, and section clashes against current assignments |
| `solve_basic_backtracking()` | Searches in the original meeting order using backtracking |
| `solve_mrv_forward_checking()` | Uses MRV to select a meeting and forward checking to prune domains |
| `validate_timetable()` | Independently checks completeness, domain membership, and clash constraints |
| `display_timetable()` | Prints the resulting schedule grouped by section and time |
| `export_timetable()` | Writes the final timetable to a CSV file |
| `run_experiments()` | Runs repeated comparisons and saves experiment data |
| `create_charts()` | Creates the three algorithm comparison charts |
| `main()` | Coordinates the complete application workflow |

## 5.2 Input data

The sample JSON data defines:

- 20 weekly time slots: four periods per day from Monday to Friday;
- five teachers;
- four rooms: two theory rooms and two computer laboratories;
- five courses;
- three student sections: BCY-3A, BCY-3B, and BCY-3C.

| Course | Teacher | Room type | Students per section | Weekly sessions per section |
|---|---|---|---:|---:|
| Artificial Intelligence | Dr. Ahmed | Lab | 30 | 1 |
| Database Systems | Ms. Sara | Theory | 35 | 1 |
| Operating Systems | Mr. Bilal | Theory | 32 | 1 |
| Computer Networks | Dr. Hina | Lab | 28 | 1 |
| Cyber Security | Mr. Usman | Theory | 40 | 1 |

The `load_data()` function enforces the maximum of five courses and five distinct sections. It also checks that at least one time slot exists, slot IDs are unique, each course refers to an existing teacher, and each course has at least one weekly session.

## 5.3 Domain generation

The `create_domains()` function loops through every meeting, every time slot, and every room. It first checks the teacher's availability. It then checks room type, room capacity, and room availability. Only combinations that pass these tests are stored in the meeting's domain.

This step reduces the search space before the recursive algorithms begin. It also separates resource suitability from the clash checks performed during assignment.

## 5.4 Timetable validation

After the enhanced solver returns an assignment, `validate_timetable()` checks that:

1. every meeting has been assigned;
2. the assigned value belongs to that meeting's original domain; and
3. no assigned meeting conflicts with another meeting under the teacher, room, or section rules.

The timetable is displayed and exported only when the enhanced solution passes this independent validation.

# 6. Search Algorithms

## 6.1 Basic backtracking

Basic backtracking is the baseline algorithm. It considers meetings in their existing list order. For the current meeting, it tries domain values one by one. If a value is consistent with the existing partial assignment, it assigns that value and recursively attempts to schedule the next meeting.

If a later meeting cannot be assigned, the algorithm removes the earlier assignment and tries another value. This undo operation is called backtracking. Search ends successfully when every meeting has been assigned.

**Simplified pseudocode:**

```text
BACKTRACK(index):
    if index equals number of meetings:
        return success

    meeting = meetings[index]

    for each value in domain[meeting]:
        count one attempted assignment
        if value satisfies current constraints:
            assign value to meeting
            if BACKTRACK(index + 1) succeeds:
                return success
            remove the assignment

    count a backtrack
    return failure
```

## 6.2 Minimum Remaining Values (MRV)

MRV changes the order in which variables are selected. Instead of always selecting the next meeting in the original list, it chooses the unassigned meeting with the smallest current domain.

The purpose is to handle the most constrained meeting first. If a meeting has very few legal choices, postponing it may cause the search to fail late. MRV attempts to expose such problems earlier.

In the code, the selection is performed using Python's `min()` function and the length of each unassigned meeting's current domain.

## 6.3 Forward checking

After a meeting is assigned, forward checking examines the domains of all remaining unassigned meetings. It removes any values that conflict with the new assignment. If a remaining meeting's domain becomes empty, the current path cannot lead to a complete timetable, so the algorithm backtracks immediately.

The implementation creates new domain lists at each recursive step. This preserves the parent search state's domains, allowing the algorithm to try another value after backtracking without permanently losing previously available choices.

## 6.4 Combined MRV and forward checking

The enhanced solver follows this process:

1. Select the unassigned meeting with the fewest remaining values (MRV).
2. Try one of its remaining time-room values.
3. Check that the value does not conflict with the current assignment.
4. Assign the value temporarily.
5. Remove conflicting values from the domains of remaining meetings (forward checking).
6. If any remaining domain is empty, undo the assignment and try another value.
7. Otherwise, recursively continue until all meetings are assigned.

The heuristic is not a machine-learning model. It is a search strategy based on the number of legal values remaining for each variable.

# 7. Execution and Output Files

## 7.1 Requirements

- Python 3.9 or later
- Matplotlib for generating charts

Install the dependency from the project folder:

```bash
python -m pip install -r requirements.txt
```

Run the application with:

```bash
python main.py
```

## 7.2 Execution sequence

The `main()` function locates the project directory, loads `university_data.json`, creates the domains, and stops early if any meeting has no feasible initial value. It then runs basic backtracking and the enhanced solver, prints their search statistics, validates the enhanced result, displays the timetable, and exports it to the `results` folder. Finally, it launches the 20-trial experiment and generates charts.

## 7.3 Generated files

| File | Purpose |
|---|---|
| `results/final_timetable.csv` | Final validated timetable |
| `results/experiment_results.csv` | Per-trial success, node, backtrack, and runtime data |
| `results/nodes_comparison.png` | Search nodes by trial |
| `results/runtime_comparison.png` | Runtime by trial |
| `results/success_rate_comparison.png` | Overall success-rate comparison |

# 8. Testing and Results

## 8.1 Sample execution

The sample run loaded five courses, three unique sections, 15 class meetings, and 20 time slots. Both algorithms found a complete assignment. The enhanced solver's output passed the independent validation function.

The resulting timetable contains five meetings for each section:

| Section | Course | Day | Time | Room |
|---|---|---|---|---|
| BCY-3A | Artificial Intelligence | Monday | 09:00-10:30 | Computer Lab 201 |
| BCY-3A | Computer Networks | Monday | 11:00-12:30 | Computer Lab 202 |
| BCY-3A | Database Systems | Monday | 13:00-14:30 | Lecture Room 101 |
| BCY-3A | Operating Systems | Monday | 15:00-16:30 | Lecture Room 101 |
| BCY-3A | Cyber Security | Tuesday | 09:00-10:30 | Lecture Room 101 |
| BCY-3B | Operating Systems | Monday | 09:00-10:30 | Lecture Room 101 |
| BCY-3B | Artificial Intelligence | Monday | 11:00-12:30 | Computer Lab 201 |
| BCY-3B | Computer Networks | Monday | 13:00-14:30 | Computer Lab 202 |
| BCY-3B | Cyber Security | Monday | 15:00-16:30 | Lecture Room 102 |
| BCY-3B | Database Systems | Tuesday | 09:00-10:30 | Lecture Room 102 |
| BCY-3C | Computer Networks | Monday | 09:00-10:30 | Computer Lab 202 |
| BCY-3C | Database Systems | Monday | 11:00-12:30 | Lecture Room 101 |
| BCY-3C | Artificial Intelligence | Monday | 13:00-14:30 | Computer Lab 201 |
| BCY-3C | Operating Systems | Tuesday | 11:00-12:30 | Lecture Room 101 |
| BCY-3C | Cyber Security | Tuesday | 13:00-14:30 | Lecture Room 101 |

## 8.2 Direct solver result from the recorded run

| Metric | Basic backtracking | MRV + forward checking |
|---|---:|---:|
| Solution found | Yes | Yes |
| Search nodes | 85 | 15 |
| Backtracks | 0 | 0 |
| Runtime | 0.0542 ms | 1.8609 ms |

These figures describe one direct run on the supplied sample data. Runtime is machine- and execution-dependent and should not be interpreted as a universal benchmark.

## 8.3 Repeated-trial experiment

The experiment runner performs 20 trials. For each trial, it uses a deterministic seed to shuffle the meeting order and the order of the values in each domain. Both algorithms receive the same shuffled order for that trial. The underlying university dataset remains unchanged.

**Important interpretation:** these are 20 repeated trials of one sample scheduling problem, not 20 different generated university instances. The current experiment therefore measures the effect of search ordering on this dataset; it does not yet provide a scalability test across increasing problem sizes.

The recorded averages were:

| Metric (20 trials) | Basic backtracking | MRV + forward checking |
|---|---:|---:|
| Successful trials | 20 / 20 | 20 / 20 |
| Average search nodes | 18.90 | 15.00 |
| Average backtracks | 0.00 | 0.00 |
| Average runtime | 0.0138 ms | 1.7046 ms |

MRV with forward checking attempted 3.90 fewer nodes per trial on average, approximately 20.6% fewer than basic backtracking for this particular experiment. However, its average measured runtime was higher because MRV selection and forward-checking domain filtering introduce additional work. The search problem is small and easy enough that this overhead dominates the time measurement.

## 8.4 Charts

### Search node comparison

![Search node comparison over 20 trials](Timetable_Report_Assets/nodes_comparison.png)

The chart shows the number of attempted assignments in each trial. MRV with forward checking used 15 nodes in each recorded trial, while the baseline varied with the shuffled search order.

\newpage

### Runtime comparison

![Runtime comparison over 20 trials](Timetable_Report_Assets/runtime_comparison.png)

The enhanced algorithm took longer on this small sample. Forward checking can reduce search work, but it also needs to examine and filter the remaining domains after assignments.

\newpage

### Success-rate comparison

![Success-rate comparison over 20 trials](Timetable_Report_Assets/success_rate_comparison.png)

Both approaches completed all 20 trials, resulting in a 100% success rate for this feasible sample dataset. This does not establish that both algorithms will always succeed on larger or infeasible datasets.

# 9. Evaluation and Discussion

The sample execution demonstrates that the program can read its local dataset, create the required meeting variables, construct legal domains, find a complete timetable, validate it, and export the result. The repeated trials also demonstrate that the program can collect comparable search statistics for both solvers.

The results illustrate an important distinction between search effort and execution time. MRV with forward checking reduced the average number of attempted assignments in the recorded trials. However, the enhanced solver performs additional operations to select the smallest domain and to filter remaining domains. On a small problem, this overhead can exceed the time saved by reducing search nodes.

The sample is feasible and relatively unconstrained. No trial required a backtrack, and both solvers achieved a 100% success rate. Consequently, this test is useful as a functional demonstration but is not sufficient to demonstrate how the algorithms behave on difficult, heavily constrained, or impossible scheduling instances.

# 10. Limitations and Difference from the Evaluation Plan

The original project proposal described a comparison using at least 20 generated instances of increasing size and constraint density, with the same instances solved by both algorithms. The current code instead repeats one sample dataset 20 times with shuffled meeting and domain orders. This is a narrower experiment and should be described as such in any presentation or submission.

Other current limitations include:

- The hard limit is five courses and five distinct sections; the included sample uses five courses and three sections.
- There is no generator for larger datasets or for systematically increasing constraint density.
- The conflict checker compares time-slot IDs. It assumes the defined slots are distinct, non-overlapping periods and does not calculate arbitrary interval overlap.
- The current output does not optimize soft constraints such as teacher preferences, gaps, or balanced workloads.
- The program is a command-line tool and does not provide a GUI, database, or live university integration.
- The sample availability fields are omitted, so teachers and rooms default to availability in every defined slot.
- The current sample assigns a distinct teacher to each course, so it does not strongly stress-test teacher conflicts between different courses.

These limitations do not invalidate the sample schedule, but they restrict the conclusions that can be drawn from the experiment.

# 11. Future Improvements

The following changes would make the project more comprehensive:

1. Generate multiple datasets with increasing numbers of courses, sections, rooms, and time slots, while respecting the current project limits or revising them deliberately.
2. Increase constraint density by varying teacher availability, room availability, room capacity, and room type requirements.
3. Run both algorithms on exactly the same generated datasets and record the random seeds.
4. Repeat timing measurements and report a median or average, especially for very short runtimes.
5. Add infeasible test cases to verify that the solver correctly reports when no timetable can be found.
6. Extend conflict detection to compare actual start and end times if arbitrary or overlapping time periods are allowed.
7. Add optional soft constraints, such as preferred teaching times and balanced daily schedules.
8. Add a simple graphical interface or timetable calendar view after the core CSP logic is stable.

# 12. Conclusion

The AI-Based University Timetable Generator demonstrates how a real-world scheduling task can be represented and solved as a Constraint Satisfaction Problem. The application uses each required course-section meeting as a variable, creates domains of feasible time-room assignments, and enforces teacher, room, and section conflict rules alongside availability, capacity, and room-type restrictions.

The project implements basic backtracking as a baseline and an enhanced solver using MRV and forward checking. On the supplied sample dataset, both algorithms generated valid timetables. Across 20 repeated trials of that same dataset, the enhanced solver attempted fewer assignments on average but required more runtime because of its additional domain-processing overhead. The results show why both search effort and runtime should be measured rather than assuming that one metric guarantees better overall performance.

The current implementation provides a compact, understandable foundation for a single-developer AI laboratory project. A broader experiment with generated datasets of increasing size and difficulty is the most important next step for evaluating scalability.

# References and Project Materials

1. *AI-Based University Timetable Generator - Project Proposal*, AL-2002 Artificial Intelligence (Laboratory), Fall 2026. Used as the project-planning and problem-formulation source.
2. `main.py` - Python implementation of the CSP model, search algorithms, validation, exports, and experiments.
3. `university_data.json` - Local synthetic sample dataset.
4. `README.md` - Project setup and execution instructions.
5. Python standard library modules used by the project: `csv`, `json`, `os`, `random`, and `time`.
6. Matplotlib - Used to generate experiment comparison charts.

