# FAST — National University of Computer and Emerging Sciences

**FAST School of Computing · Karachi Campus · Department of Artificial Intelligence & Data Science**  
**AL-2002 Artificial Intelligence (Laboratory) · Fall 2026**

# Project Proposal

*Semester Lab Project · Weightage 1 mark*

## Group Information

| Role | Name | Roll Number | Section | Role in the project |
|---|---|---|---|---|
| Leader | Hassan Gohar | 24K-2033 | BCY-5A | CSP solver, integration, Data model, testing, CLI and evaluation |

## Project Details

| Field | Details |
|---|---|
| **Project Title** | AI-Based University Timetable Generator |
| **Project Idea** | Own idea (confirm approval with instructor) |
| **Category** | Part A — Game ☐ · Part B — Applied / Data ☒ |
| **GitHub Repository URL** | — |
| **Date of Submission** | 21/10/2026 |

---

## 1. Project Title and Summary

The AI-Based University Timetable Generator creates a weekly university class schedule by assigning each course meeting to a time slot, classroom, and teacher while respecting university rules. It is intended for academic coordinators and department staff who currently prepare schedules manually or revise them after discovering clashes. The system models timetable construction as a Constraint Satisfaction Problem (CSP), where variables represent class meetings and domains contain possible time-room assignments. A backtracking search algorithm enhanced with Minimum Remaining Values (MRV) and forward checking will search for a valid schedule. The program will print the timetable and a conflict/performance report in the command-line interface (CLI), and compare the enhanced search with a simpler baseline.

## 2. Problem Statement and Motivation

Preparing a university timetable is difficult because many assignments must be made together rather than independently. Each course meeting needs a time, room, and instructor, but a teacher cannot teach two classes at once, a room cannot host two classes simultaneously, and students in the same section cannot attend overlapping classes. Room capacity, room type for laboratories, and the required number of weekly meetings add further restrictions. A choice that looks valid early in the process can leave a later course with no available slot, forcing the scheduler to undo earlier choices. As the number of courses, rooms, teachers, sections, and time slots grows, the number of possible schedules grows combinatorially; trying every combination is inefficient. Departments often rely on spreadsheets and repeated manual adjustments, which can be slow and can introduce overlooked conflicts. This project will represent the scheduling task as a Constraint Satisfaction Problem and use search heuristics to reduce unnecessary exploration. A reliable timetable generator can reduce manual effort, make conflicts easier to detect, and provide a repeatable way to compare scheduling strategies.

## 3. Problem Formulation

### 3.1 PEAS Description

| Component | Description for the project |
|---|---|
| **Performance measure** | Generate a complete valid timetable; minimize hard-constraint violations (target: 0), search nodes, backtracks, and runtime. |
| **Environment** | A simulated university with courses/class meetings, teachers, student sections, rooms, room capacities/types, and discrete weekly time slots. |
| **Actuators** | Assign a class meeting to a time slot and room; backtrack/revise assignments; print the timetable and evaluation report. |
| **Sensors** | Read the local input data and current partial assignments; inspect domains and detect teacher, room, section, capacity, and room-type conflicts. |

### 3.2 Environment and Agent Type

| Property | Classification |
|---|---|
| **Observability** | Fully observable ☒ · Partially observable ☐ |
| **Determinism** | Deterministic ☒ · Stochastic ☐ |
| **Change over time** | Static ☒ · Dynamic ☐ |
| **State and actions** | Discrete ☒ · Continuous ☐ |
| **Agents** | Single-agent ☒ · Multi-agent / adversarial ☐ |
| **Agent type** | Simple reflex ☐ · Model-based ☒ · Goal-based ☒ · Utility-based ☐ · Learning ☐ |

### 3.3 Problem Representation

| Element | Representation |
|---|---|
| **State representation** | A partial assignment of each class meeting to a (day, period, room) combination, plus the remaining legal domain for each unassigned meeting. |
| **Actions / moves** | Select an unassigned meeting and assign one legal time-room value; remove inconsistent values from future domains; backtrack if a domain becomes empty. |
| **Initial state** | All class meetings are unassigned; each variable begins with the time-room combinations permitted by room capacity/type and availability. |
| **Goal or terminal test** | Every required class meeting is assigned and all hard constraints are satisfied. |
| **Cost, utility, fitness or evaluation** | Primary objective: zero hard-constraint violations. Compare nodes explored, backtracks, runtime, and schedule completion rate; optional soft preferences may be reported but are not required for the core version. |

## 4. Proposed AI Approach

| # | Technique | Role in the project | Own code or library |
|---:|---|---|---|
| 1 | Backtracking CSP search | Assigns class meetings one at a time and undoes a choice when it causes a dead end. | Own code |
| 2 | MRV + forward checking | Chooses the unassigned meeting with the fewest legal values and removes incompatible values from neighboring domains. | Own code |
| 3 | Constraint validator / evaluator | Checks teacher, room, section, capacity, room-type, and required-meeting constraints and counts search statistics. | Own code |
| B | Baseline: Plain backtracking | Same CSP without MRV or forward checking; used to compare search effort. | Own code |

Timetabling naturally fits a CSP: each required class meeting is a variable, its domain contains feasible time-slot and room combinations, and constraints rule out incompatible assignments. The main solver will use backtracking search. MRV selects the unassigned meeting with the smallest remaining legal domain, so the solver addresses the most constrained meeting first. Forward checking then removes values that conflict with a new assignment from the domains of related unassigned meetings; if any domain becomes empty, the solver backtracks early. The heuristic is therefore based on the number of legal values remaining, not on a learned model. As a baseline, plain backtracking without MRV or forward checking will solve the same generated instances. Both approaches will use the same constraints and input seeds, and their completion rate, nodes explored, backtracks, and runtime will be compared. All search and constraint logic will be implemented by the team.

### 4.1 Planned Class Design

- **Course:** `course_id`, `name`, `section_id`, `teacher_id`, `meetings_per_week`, `required_room_type`, `expected_enrolment`; describes a course and its scheduling needs.
- **Teacher:** `teacher_id`, `name`, `available_slots`; stores instructor availability and identifies teacher clashes.
- **Room:** `room_id`, `capacity`, `room_type`, `available_slots`; stores room suitability and availability.
- **TimeSlot:** `day`, `period`, `start_time`, `end_time`; represents one discrete teaching period.
- **ClassMeeting:** `meeting_id`, `course_id`, `meeting_index`; represents one required occurrence of a course and becomes a CSP variable.
- **TimetableCSP:** `meetings`, `teachers`, `rooms`, `time_slots`, `domains`, `constraints`; builds legal domains and validates partial/full assignments.
- **TimetableSolver:** search statistics and current assignment; implements plain backtracking and the MRV + forward-checking solver.

**Relationships:** Course creates one or more ClassMeeting objects; each ClassMeeting references a Course; TimetableCSP uses Teacher, Room, and TimeSlot data; TimetableSolver searches and returns assignments validated by TimetableCSP.

## 5. Scope

| # | Feature | Why it is essential |
|---:|---|---|
| 1 | Load a small, locally stored university dataset | The solver needs courses, teachers, sections, rooms, and time slots. |
| 2 | Model hard constraints | Prevents teacher, room, and section overlaps and enforces room capacity/type and required meetings. |
| 3 | Generate schedules with plain backtracking and enhanced CSP search | Provides a baseline and the main AI technique for comparison. |
| 4 | Print timetable by section and a scheduling/conflict report in the CLI | Makes results understandable and demonstrable without a GUI. |
| 5 | Run repeatable experiments and report search statistics | Provides evidence that the AI approach works and supports evaluation. |

The project will not include a web application, user accounts, a database server, live integration with university systems, automatic enrolment, multiple campuses, real-time changes during a semester, or machine-learning-based prediction. Advanced optimization of teacher preferences and soft constraints will be optional only if the core solver is complete. The initial version will use a controlled, simulated dataset and a CLI.

## 6. Data or Environment Source

| Field | Details |
|---|---|
| **Source name and URL** | Generated locally by the project team; no external URL or dataset is required. |
| **Type** | Public dataset ☐ · Web API ☐ · Self-collected ☐ · Generated / simulated ☒ |
| **Access requirements** | No key needed ☒ · Free key required ☐ |
| **Approximate size** | Initial test scenario: about 8–20 courses/class meetings, 5–10 teachers, 4–8 rooms, 2–4 sections, and 20–30 weekly time slots; larger seeded instances for experiments. |
| **Licence / terms of use** | Original synthetic data created by the team; no third-party dataset licence applies. |
| **Offline fallback** | All scenarios will be stored as local CSV or JSON files. A fixed random seed will be recorded for generated test instances, so every experiment can be repeated offline. |

## 7. Evaluation Plan

| Item | Plan |
|---|---|
| **What will be compared** | Plain backtracking vs. backtracking with MRV and forward checking. |
| **Metric(s)** | Completion/success rate; hard-constraint violations; search nodes explored; backtracks; runtime in seconds. |
| **Baseline** | Plain backtracking with the same variable/domain definitions and constraint checks, without MRV or forward checking. |
| **Test instances / test set** | At least 20 generated instances of increasing size and constraint density; use identical instances for both solvers. |
| **Number of runs and seed** | One deterministic run per solver per fixed instance, with recorded seeds; repeat timing runs 3 times if runtime noise is noticeable and report the median. |
| **Planned charts (at least three)** | 1. Nodes explored by solver and instance size. 2. Runtime by solver and instance size. 3. Success rate by instance size. Optional: backtracks by solver. |

## 8. Division of Work

| Member | Modules / components owned | Approximate share |
|---|---|---:|
| Member 1 / Leader | CSP model, constraints, plain backtracking, MRV and forward checking; input scenarios, CLI display, experiment runner, tests, charts and documentation | 100% |

## 9. Milestones and Timeline

| # | Milestone — what will be demonstrably working | Target date | Owner |
|---:|---|---|---|
| 1 | Input data model and constraint validator run on sample cases | Week 11 | Member 1 |
| 2 | Plain backtracking produces a valid schedule on small cases | Week 12 | Member 1 |
| 3 | MRV and forward checking integrated; dead ends trigger backtracking | Week 13 | Member 1 + M |
| 4 | CLI timetable/report and repeatable experiment runner working | Week 14 | Member 2 |
| 5 | Experiments complete, final integration, documentation and repository cleanup | Week 15 | Both members |

## 10. Expected Outcome and Risks

The finished program will run from the command line, load a local simulated university dataset, and print a weekly timetable grouped by section, along with the number of scheduled meetings, unscheduled meetings, constraint violations, search nodes, backtracks, and runtime. The expected outcome is a valid schedule for feasible instances and clear reporting when a schedule cannot be found within the search process. MRV and forward checking are expected to reduce search effort on constrained instances, although the improvement will be measured rather than assumed. The main risks are a large search space and incorrectly implemented constraints. If search is too slow, test smaller instances and improve variable ordering; if validation bugs appear, add small unit tests for each constraint and cross-check solver output independently.

---

## For Office Use — Lab Instructor

| Field | Details |
|---|---|
| **Proposal status** | Approved ☐ · Approved with changes ☐ · Revision required ☐ |
| **Comments** |  |
| **Signature and date** |  |

---

*End of Project Proposal*  
*AL-2002 · Fall 2026 · Page 5 of 5 in the original proposal*
