"""AI-Based University Timetable Generator

A beginner-friendly CSP project using:
1. Basic backtracking search
2. Backtracking with MRV and forward checking

The project is intentionally kept in one Python file so it is easier to
understand, explain, and demonstrate in a viva.
"""

import csv
import json
import os
import random
import time


# ------------------------------------------------------------
# 1. SIMPLE CLASSES
# ------------------------------------------------------------

class Course:
    def __init__(self, course_id, name, teacher_id, sections,
                 students, room_type, sessions_per_week):
        self.course_id = course_id
        self.name = name
        self.teacher_id = teacher_id
        self.sections = sections
        self.students = students
        self.room_type = room_type
        self.sessions_per_week = sessions_per_week


class Teacher:
    def __init__(self, teacher_id, name, available_slots):
        self.teacher_id = teacher_id
        self.name = name
        self.available_slots = available_slots


class Room:
    def __init__(self, room_id, name, capacity, room_type, available_slots):
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type
        self.available_slots = available_slots


class Meeting:
    """One scheduled meeting of one course for one student section."""
    def __init__(self, meeting_id, course, section, session_number):
        self.meeting_id = meeting_id
        self.course = course
        self.section = section
        self.session_number = session_number


# ------------------------------------------------------------
# 2. LOAD DATA AND CREATE MEETINGS
# ------------------------------------------------------------

def load_data(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        data = json.load(file)

    if len(data["courses"]) > 5:
        raise ValueError("The project allows a maximum of 5 courses.")

    section_names = set()
    for course_data in data["courses"]:
        for section in course_data["sections"]:
            section_names.add(section)

    if len(section_names) > 5:
        raise ValueError("The project allows a maximum of 5 student sections.")

    if not data["time_slots"]:
        raise ValueError("At least one time slot must be provided.")

    slot_ids = [slot["id"] for slot in data["time_slots"]]
    if len(slot_ids) != len(set(slot_ids)):
        raise ValueError("Every time slot must have a unique ID.")

    teachers = {}
    for item in data["teachers"]:
        available = item.get("available_slots", slot_ids)
        teachers[item["id"]] = Teacher(item["id"], item["name"], available)

    rooms = []
    for item in data["rooms"]:
        available = item.get("available_slots", slot_ids)
        rooms.append(Room(item["id"], item["name"], item["capacity"],
                          item["room_type"], available))

    courses = []
    for item in data["courses"]:
        if item["teacher_id"] not in teachers:
            raise ValueError("Teacher not found for course: " + item["id"])
        if item["sessions_per_week"] < 1:
            raise ValueError("Each course must have at least one weekly session.")

        course = Course(
            item["id"], item["name"], item["teacher_id"], item["sections"],
            item["students"], item["room_type"], item["sessions_per_week"]
        )
        courses.append(course)

    meetings = []
    for course in courses:
        for section in course.sections:
            for session in range(1, course.sessions_per_week + 1):
                meeting_id = course.course_id + "_" + section + "_" + str(session)
                meetings.append(Meeting(meeting_id, course, section, session))

    return data["time_slots"], teachers, rooms, courses, meetings, section_names


# ------------------------------------------------------------
# 3. CREATE DOMAINS
# ------------------------------------------------------------

def create_domains(meetings, teachers, rooms, time_slots):
    """Create legal (time slot, room) choices for every meeting."""
    domains = {}

    for meeting in meetings:
        teacher = teachers[meeting.course.teacher_id]
        possible_values = []

        for slot in time_slots:
            # A teacher must be available at this time.
            if slot["id"] not in teacher.available_slots:
                continue

            for room in rooms:
                # Room must have the correct type and enough capacity.
                if room.room_type != meeting.course.room_type:
                    continue
                if room.capacity < meeting.course.students:
                    continue
                if slot["id"] not in room.available_slots:
                    continue

                possible_values.append({
                    "slot_id": slot["id"],
                    "day": slot["day"],
                    "start": slot["start"],
                    "end": slot["end"],
                    "room_id": room.room_id,
                    "room_name": room.name
                })

        domains[meeting.meeting_id] = possible_values

    return domains


# ------------------------------------------------------------
# 4. CHECK CONSTRAINTS
# ------------------------------------------------------------

def is_valid(meeting, value, assignment, meeting_lookup):
    """Return False if this choice creates a teacher, room, or section clash."""

    for other_id, other_value in assignment.items():
        other_meeting = meeting_lookup[other_id]

        # Two meetings in different time slots cannot clash.
        if value["slot_id"] != other_value["slot_id"]:
            continue

        # Constraint 1: a teacher cannot teach two classes at once.
        if meeting.course.teacher_id == other_meeting.course.teacher_id:
            return False

        # Constraint 2: a room cannot be used by two classes at once.
        if value["room_id"] == other_value["room_id"]:
            return False

        # Constraint 3: a student section cannot attend two classes at once.
        if meeting.section == other_meeting.section:
            return False

    return True


# ------------------------------------------------------------
# 5. BASIC BACKTRACKING
# ------------------------------------------------------------

def solve_basic_backtracking(meetings, domains):
    """Assign meetings in their original order, using backtracking."""
    assignment = {}
    meeting_lookup = {meeting.meeting_id: meeting for meeting in meetings}
    stats = {"nodes": 0, "backtracks": 0}

    def search(index):
        # All meetings have been assigned successfully.
        if index == len(meetings):
            return True

        meeting = meetings[index]

        for value in domains[meeting.meeting_id]:
            stats["nodes"] += 1

            if is_valid(meeting, value, assignment, meeting_lookup):
                assignment[meeting.meeting_id] = value

                if search(index + 1):
                    return True

                # The choice caused a dead end. Undo it.
                del assignment[meeting.meeting_id]

        stats["backtracks"] += 1
        return False

    start_time = time.perf_counter()
    solved = search(0)
    elapsed = time.perf_counter() - start_time

    return (assignment.copy() if solved else None), stats, elapsed


# ------------------------------------------------------------
# 6. MRV + FORWARD CHECKING
# ------------------------------------------------------------

def solve_mrv_forward_checking(meetings, domains):
    """Use MRV to choose a meeting and forward checking to prune domains."""
    assignment = {}
    meeting_lookup = {meeting.meeting_id: meeting for meeting in meetings}
    stats = {"nodes": 0, "backtracks": 0}

    def search(unassigned, current_domains):
        if len(unassigned) == 0:
            return True

        # MRV: choose the meeting with the fewest remaining legal choices.
        selected = min(
            unassigned,
            key=lambda meeting: len(current_domains[meeting.meeting_id])
        )

        selected_id = selected.meeting_id
        if len(current_domains[selected_id]) == 0:
            stats["backtracks"] += 1
            return False

        for value in current_domains[selected_id]:
            stats["nodes"] += 1

            if not is_valid(selected, value, assignment, meeting_lookup):
                continue

            assignment[selected_id] = value
            new_unassigned = [m for m in unassigned if m.meeting_id != selected_id]

            # Forward checking: remove choices that now conflict with this
            # assignment from the domains of all remaining meetings.
            new_domains = {}
            domain_failed = False

            for other in new_unassigned:
                other_id = other.meeting_id
                filtered_values = []

                for other_value in current_domains[other_id]:
                    if is_valid(other, other_value, assignment, meeting_lookup):
                        filtered_values.append(other_value)

                new_domains[other_id] = filtered_values

                # An empty domain means this path cannot lead to a solution.
                if len(filtered_values) == 0:
                    domain_failed = True
                    break

            if not domain_failed:
                if search(new_unassigned, new_domains):
                    return True

            # Backtrack: remove the current assignment and try another value.
            del assignment[selected_id]

        stats["backtracks"] += 1
        return False

    # Make fresh domain lists so the original domains remain unchanged.
    starting_domains = {key: list(values) for key, values in domains.items()}

    start_time = time.perf_counter()
    solved = search(list(meetings), starting_domains)
    elapsed = time.perf_counter() - start_time

    return (assignment.copy() if solved else None), stats, elapsed


# ------------------------------------------------------------
# 7. INDEPENDENTLY VALIDATE THE FINAL TIMETABLE
# ------------------------------------------------------------

def validate_timetable(meetings, assignment, domains):
    """Check completeness, legal domains, and all three clash constraints."""
    if assignment is None or len(assignment) != len(meetings):
        return False

    meeting_lookup = {meeting.meeting_id: meeting for meeting in meetings}

    for meeting in meetings:
        meeting_id = meeting.meeting_id
        if meeting_id not in assignment:
            return False
        if assignment[meeting_id] not in domains[meeting_id]:
            return False

    # Check every assigned meeting against all the other assigned meetings.
    for meeting in meetings:
        other_assignments = {
            other_id: value
            for other_id, value in assignment.items()
            if other_id != meeting.meeting_id
        }
        if not is_valid(meeting, assignment[meeting.meeting_id],
                        other_assignments, meeting_lookup):
            return False

    return True


# ------------------------------------------------------------
# 8. DISPLAY AND EXPORT THE TIMETABLE
# ------------------------------------------------------------

def display_timetable(meetings, assignment, teachers):
    day_order = {"Monday": 1, "Tuesday": 2, "Wednesday": 3,
                 "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}

    rows = []
    for meeting in meetings:
        value = assignment[meeting.meeting_id]
        rows.append((meeting, value))

    rows.sort(key=lambda item: (
        item[0].section,
        day_order.get(item[1]["day"], 99),
        item[1]["start"]
    ))

    print("\nFINAL TIMETABLE")
    print("-" * 92)
    print("{:<10} {:<27} {:<13} {:<11} {:<8} {:<8} {}".format(
        "SECTION", "COURSE", "DAY", "START", "END", "ROOM", "TEACHER"
    ))
    print("-" * 92)

    for meeting, value in rows:
        teacher_name = teachers[meeting.course.teacher_id].name
        print("{:<10} {:<27} {:<13} {:<11} {:<8} {:<8} {}".format(
            meeting.section,
            meeting.course.name[:26],
            value["day"],
            value["start"],
            value["end"],
            value["room_name"],
            teacher_name
        ))

    print("-" * 92)


def export_timetable(meetings, assignment, output_file, teachers):
    fields = ["section", "course_id", "course_name", "teacher_id", "teacher_name",
              "day", "start", "end", "room_id", "room_name"]

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for meeting in meetings:
            value = assignment[meeting.meeting_id]
            writer.writerow({
                "section": meeting.section,
                "course_id": meeting.course.course_id,
                "course_name": meeting.course.name,
                "teacher_id": meeting.course.teacher_id,
                "teacher_name": teachers[meeting.course.teacher_id].name,
                "day": value["day"],
                "start": value["start"],
                "end": value["end"],
                "room_id": value["room_id"],
                "room_name": value["room_name"]
            })


# ------------------------------------------------------------
# 9. RUN 20 EXPERIMENTS
# ------------------------------------------------------------

def run_experiments(meetings, original_domains, number_of_trials, results_folder):
    """Repeat the same problem with shuffled search orders.

    These are repeated trials of the same dataset, not 20 different
    universities. Shuffling lets us compare how search order affects each
    algorithm while keeping the scheduling problem itself unchanged.
    """
    results = []

    for trial in range(1, number_of_trials + 1):
        random_generator = random.Random(1000 + trial)

        # Both algorithms receive the same shuffled meeting and value order.
        shuffled_meetings = list(meetings)
        random_generator.shuffle(shuffled_meetings)

        shuffled_domains = {}
        for meeting in meetings:
            values = list(original_domains[meeting.meeting_id])
            random_generator.shuffle(values)
            shuffled_domains[meeting.meeting_id] = values

        # Basic backtracking experiment.
        basic_solution, basic_stats, basic_time = solve_basic_backtracking(
            shuffled_meetings, shuffled_domains
        )
        results.append({
            "trial": trial,
            "algorithm": "Basic Backtracking",
            "success": basic_solution is not None,
            "nodes": basic_stats["nodes"],
            "backtracks": basic_stats["backtracks"],
            "runtime_ms": round(basic_time * 1000, 4)
        })

        # MRV + forward checking experiment.
        improved_solution, improved_stats, improved_time = solve_mrv_forward_checking(
            shuffled_meetings, shuffled_domains
        )
        results.append({
            "trial": trial,
            "algorithm": "MRV + Forward Checking",
            "success": improved_solution is not None,
            "nodes": improved_stats["nodes"],
            "backtracks": improved_stats["backtracks"],
            "runtime_ms": round(improved_time * 1000, 4)
        })

    results_file = os.path.join(results_folder, "experiment_results.csv")
    with open(results_file, "w", newline="", encoding="utf-8") as file:
        fields = ["trial", "algorithm", "success", "nodes", "backtracks", "runtime_ms"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print_experiment_summary(results, number_of_trials)
    create_charts(results, results_folder)
    return results


def print_experiment_summary(results, number_of_trials):
    print("\nEXPERIMENT SUMMARY")
    print("-" * 66)

    for algorithm in ["Basic Backtracking", "MRV + Forward Checking"]:
        selected = [row for row in results if row["algorithm"] == algorithm]
        average_nodes = sum(row["nodes"] for row in selected) / len(selected)
        average_time = sum(row["runtime_ms"] for row in selected) / len(selected)
        successful = sum(1 for row in selected if row["success"])

        print(algorithm)
        print("  Successful trials: {}/{}".format(successful, number_of_trials))
        print("  Average search nodes: {:.2f}".format(average_nodes))
        print("  Average runtime: {:.4f} ms".format(average_time))

    print("-" * 66)


def create_charts(results, results_folder):
    """Create three comparison charts. Matplotlib is required for charts."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib is not installed. Charts were not created.")
        print("Install it using: python -m pip install matplotlib")
        
        return

    algorithms = ["Basic Backtracking", "MRV + Forward Checking"]
    basic = [row for row in results if row["algorithm"] == algorithms[0]]
    improved = [row for row in results if row["algorithm"] == algorithms[1]]

    # Chart 1: search nodes in each trial.
    trials = [row["trial"] for row in basic]
    plt.figure(figsize=(10, 5))
    plt.plot(trials, [row["nodes"] for row in basic], marker="o",
             label=algorithms[0])
    plt.plot(trials, [row["nodes"] for row in improved], marker="o",
             label=algorithms[1])
    plt.xlabel("Trial")
    plt.ylabel("Search nodes (attempted assignments)")
    plt.title("Search Node Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, "nodes_comparison.png"))
    plt.close()

    # Chart 2: runtime in each trial.
    plt.figure(figsize=(10, 5))
    plt.plot(trials, [row["runtime_ms"] for row in basic], marker="o",
             label=algorithms[0])
    plt.plot(trials, [row["runtime_ms"] for row in improved], marker="o",
             label=algorithms[1])
    plt.xlabel("Trial")
    plt.ylabel("Runtime (milliseconds)")
    plt.title("Runtime Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, "runtime_comparison.png"))
    plt.close()

    # Chart 3: success rate across all trials.
    success_rates = [
        100 * sum(1 for row in basic if row["success"]) / len(basic),
        100 * sum(1 for row in improved if row["success"]) / len(improved)
    ]
    plt.figure(figsize=(8, 5))
    plt.bar(algorithms, success_rates)
    plt.ylabel("Successful trials (%)")
    plt.title("Success Rate Comparison")
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, "success_rate_comparison.png"))
    plt.close()

    print("Charts saved in the results folder.")


# ------------------------------------------------------------
# 10. MAIN PROGRAM
# ------------------------------------------------------------

def main():
    project_folder = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(project_folder, "university_data.json")
    results_folder = os.path.join(project_folder, "results")
    os.makedirs(results_folder, exist_ok=True)

    time_slots, teachers, rooms, courses, meetings, sections = load_data(data_file)
    domains = create_domains(meetings, teachers, rooms, time_slots)

    print("AI-BASED UNIVERSITY TIMETABLE GENERATOR")
    print("=" * 45)
    print("Courses:", len(courses), "(maximum 5)")
    print("Student sections:", len(sections), "(maximum 5)")
    print("Class meetings to schedule:", len(meetings))
    print("Available time slots:", len(time_slots))

    # Stop early if any meeting has no possible room/time combination.
    for meeting in meetings:
        if len(domains[meeting.meeting_id]) == 0:
            print("No possible time/room choices for:", meeting.meeting_id)
            print("Check teacher availability, room type, and room capacity.")
            return

    print("\nRunning basic backtracking...")
    basic_solution, basic_stats, basic_time = solve_basic_backtracking(meetings, domains)
    print("Basic backtracking solved:", basic_solution is not None)
    print("Search nodes:", basic_stats["nodes"])
    print("Backtracks:", basic_stats["backtracks"])
    print("Runtime: {:.4f} ms".format(basic_time * 1000))

    print("\nRunning MRV + forward checking...")
    improved_solution, improved_stats, improved_time = solve_mrv_forward_checking(
        meetings, domains
    )
    print("Improved solver solved:", improved_solution is not None)
    print("Search nodes:", improved_stats["nodes"])
    print("Backtracks:", improved_stats["backtracks"])
    print("Runtime: {:.4f} ms".format(improved_time * 1000))

    if improved_solution is None:
        print("No valid timetable was found. Review the available rooms and slots.")
    elif validate_timetable(meetings, improved_solution, domains):
        print("\nIndependent validation: PASSED")
        display_timetable(meetings, improved_solution, teachers)
        timetable_file = os.path.join(results_folder, "final_timetable.csv")
        export_timetable(meetings, improved_solution, timetable_file, teachers)
        print("Timetable CSV saved to:", timetable_file)
    else:
        print("Independent validation: FAILED. Do not use this timetable.")

    # Run 20 trials to compare the two algorithms.
    run_experiments(meetings, domains, 20, results_folder)
    print("\nAll results are available in:", results_folder)


if __name__ == "__main__":
    main()
