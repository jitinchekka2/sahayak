"""
Synthetic Data Generator for Student Database
Generates realistic student data for parent-teacher meeting system
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid


class StudentDataGenerator:
    def __init__(self):
        self.first_names = [
            "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
            "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
            "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Abigail", "Michael",
            "Emily", "Daniel", "Elizabeth", "Jacob", "Sofia", "Logan", "Avery",
            "Jackson", "Ella", "Sebastian", "Madison", "Jack", "Scarlett", "Aiden",
            "Victoria", "Owen", "Aria", "Samuel", "Grace", "Matthew", "Chloe",
            "Joseph", "Camila", "Levi", "Penelope", "Mateo", "Riley", "David"
        ]

        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
            "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
            "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts"
        ]

        self.subjects = ["mathematics", "english", "science",
                         "social_studies", "art", "physical_education"]
        self.grades = ["A+", "A", "A-", "B+", "B",
                       "B-", "C+", "C", "C-", "D+", "D", "F"]
        self.trends = ["improving", "declining", "stable"]
        self.participation_levels = ["high", "medium", "low"]
        self.skill_levels = ["excellent", "good", "needs_improvement"]
        self.learning_styles = ["visual", "auditory", "kinesthetic", "mixed"]

        self.extracurricular_sports = [
            "Soccer", "Basketball", "Tennis", "Swimming", "Track and Field",
            "Baseball", "Volleyball", "Cross Country", "Golf", "Wrestling"
        ]

        self.extracurricular_clubs = [
            "Drama Club", "Chess Club", "Science Club", "Art Club", "Music Band",
            "Debate Team", "Student Council", "Photography Club", "Robotics Club",
            "Environmental Club", "Book Club", "Computer Programming Club"
        ]

        self.teacher_notes_templates = [
            "Shows excellent problem-solving skills",
            "Needs more confidence in oral presentations",
            "Great collaborative worker",
            "Sometimes struggles with time management",
            "Demonstrates strong leadership qualities",
            "Benefits from visual learning aids",
            "Excellent attention to detail",
            "Could improve organization skills",
            "Shows creativity in assignments",
            "Needs encouragement to participate more"
        ]

    def generate_student_id(self) -> str:
        """Generate unique student ID"""
        return f"STU_{uuid.uuid4().hex[:8].upper()}"

    def generate_birth_date(self, grade: str) -> datetime:
        """Generate birth date based on grade level"""
        grade_num = int(grade)
        age = 5 + grade_num  # Kindergarten starts at age 5
        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        return datetime(birth_year, birth_month, birth_day)

    def generate_phone(self) -> str:
        """Generate random phone number"""
        return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"

    def generate_email(self, first_name: str, last_name: str) -> str:
        """Generate email address"""
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
        return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"

    def generate_address(self) -> str:
        """Generate random address"""
        street_numbers = random.randint(100, 9999)
        street_names = ["Main St", "Oak Ave", "Pine Rd",
                        "Elm St", "Cedar Ave", "Maple Dr"]
        cities = ["Springfield", "Madison", "Franklin",
                  "Georgetown", "Clinton", "Salem"]
        states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"]

        return f"{street_numbers} {random.choice(street_names)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}"

    def generate_subject_data(self) -> Dict[str, Any]:
        """Generate academic data for a subject"""
        base_score = random.uniform(60, 100)
        trend = random.choice(self.trends)

        # Adjust score based on trend
        if trend == "improving":
            current_score = min(100, base_score + random.uniform(5, 15))
        elif trend == "declining":
            current_score = max(50, base_score - random.uniform(5, 15))
        else:
            current_score = base_score + random.uniform(-3, 3)

        # Convert score to grade
        if current_score >= 97:
            grade = "A+"
        elif current_score >= 93:
            grade = "A"
        elif current_score >= 90:
            grade = "A-"
        elif current_score >= 87:
            grade = "B+"
        elif current_score >= 83:
            grade = "B"
        elif current_score >= 80:
            grade = "B-"
        elif current_score >= 77:
            grade = "C+"
        elif current_score >= 73:
            grade = "C"
        elif current_score >= 70:
            grade = "C-"
        elif current_score >= 67:
            grade = "D+"
        elif current_score >= 65:
            grade = "D"
        else:
            grade = "F"

        return {
            "currentGrade": grade,
            "averageScore": round(current_score, 2),
            "trend": trend,
            "lastAssessmentDate": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }

    def generate_assessments(self, student_id: str, num_assessments: int = 10) -> List[Dict[str, Any]]:
        """Generate assessment records for a student"""
        assessments = []
        assessment_types = ["quiz", "test", "project", "assignment", "exam"]
        difficulties = ["easy", "medium", "hard"]

        for i in range(num_assessments):
            subject = random.choice(self.subjects)
            assessment_type = random.choice(assessment_types)
            date = datetime.now() - timedelta(days=random.randint(1, 90))

            max_score = 100 if assessment_type in [
                "test", "exam"] else random.choice([50, 75, 100])
            percentage = random.uniform(60, 100)
            score = round((percentage / 100) * max_score, 1)

            assessment = {
                "assessmentId": f"ASSESS_{uuid.uuid4().hex[:8].upper()}",
                "subject": subject,
                "type": assessment_type,
                "date": date.isoformat(),
                "score": score,
                "maxScore": max_score,
                "percentage": round(percentage, 2),
                "topics": [f"{subject.title()} Topic {j+1}" for j in range(random.randint(1, 4))],
                "teacherFeedback": random.choice(self.teacher_notes_templates),
                "timeSpent": random.randint(15, 120),
                "difficulty": random.choice(difficulties),
                "mistakes": [f"Common mistake {j+1}" for j in range(random.randint(0, 3))],
                "strengths": [f"Strength area {j+1}" for j in range(random.randint(1, 3))]
            }
            assessments.append(assessment)

        return assessments

    def generate_behavioral_incidents(self, student_id: str, num_incidents: int = 5) -> List[Dict[str, Any]]:
        """Generate behavioral incident records"""
        incidents = []
        incident_types = ["positive", "negative"]
        categories = ["participation", "discipline", "leadership",
                      "helping_others", "disruption", "tardiness"]
        severities = ["low", "medium", "high"]

        for i in range(num_incidents):
            incident_type = random.choice(incident_types)
            category = random.choice(categories)

            # Adjust category based on incident type
            if incident_type == "positive":
                category = random.choice(
                    ["participation", "leadership", "helping_others"])
            else:
                category = random.choice(
                    ["discipline", "disruption", "tardiness"])

            incident = {
                "incidentId": f"INC_{uuid.uuid4().hex[:8].upper()}",
                "date": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
                "type": incident_type,
                "category": category,
                "description": f"{incident_type.title()} incident related to {category.replace('_', ' ')}",
                "severity": random.choice(severities),
                "actionTaken": "Documented and discussed with student",
                "followUpRequired": random.choice([True, False]),
                "teacherId": f"TEACH_{uuid.uuid4().hex[:6].upper()}"
            }
            incidents.append(incident)

        return incidents

    def generate_parent_communications(self, student_id: str, num_communications: int = 3) -> List[Dict[str, Any]]:
        """Generate parent communication records"""
        communications = []
        comm_types = ["email", "phone", "meeting", "note"]
        initiators = ["teacher", "parent"]
        subjects = [
            "Academic Progress Update",
            "Behavioral Concerns",
            "Parent-Teacher Conference",
            "Assignment Missing",
            "Positive Recognition",
            "Attendance Issue"
        ]

        for i in range(num_communications):
            comm_type = random.choice(comm_types)
            subject = random.choice(subjects)

            communication = {
                "communicationId": f"COMM_{uuid.uuid4().hex[:8].upper()}",
                "date": (datetime.now() - timedelta(days=random.randint(1, 45))).isoformat(),
                "type": comm_type,
                "initiatedBy": random.choice(initiators),
                "subject": subject,
                "content": f"Discussion about {subject.lower()} - detailed communication record",
                "followUpNeeded": random.choice([True, False]),
                "followUpDate": (datetime.now() + timedelta(days=random.randint(1, 14))).isoformat(),
                "teacherId": f"TEACH_{uuid.uuid4().hex[:6].upper()}"
            }
            communications.append(communication)

        return communications

    def generate_student(self, grade: str = "5") -> Dict[str, Any]:
        """Generate complete student record"""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        student_id = self.generate_student_id()
        birth_date = self.generate_birth_date(grade)

        # Generate academic subjects data
        subjects_data = {}
        for subject in self.subjects:
            subjects_data[subject] = self.generate_subject_data()

        # Calculate overall GPA
        total_scores = [subjects_data[subject]["averageScore"]
                        for subject in subjects_data]
        gpa = sum(total_scores) / len(total_scores) / \
            25  # Convert to 4.0 scale

        student = {
            "studentId": student_id,
            "personalInfo": {
                "firstName": first_name,
                "lastName": last_name,
                "dateOfBirth": birth_date.isoformat(),
                "grade": grade,
                "section": random.choice(["A", "B", "C"]),
                "rollNumber": f"{grade}{random.randint(1, 50):02d}",
                "parentEmail": self.generate_email(first_name, last_name),
                "parentPhone": self.generate_phone(),
                "address": self.generate_address(),
                "emergencyContact": self.generate_phone()
            },
            "academicProfile": {
                "currentGPA": round(gpa, 2),
                "subjects": subjects_data,
                "strengths": random.sample([
                    "Problem solving", "Creative thinking", "Mathematical reasoning",
                    "Written communication", "Oral presentation", "Research skills",
                    "Critical analysis", "Attention to detail"
                ], k=random.randint(2, 4)),
                "areasForImprovement": random.sample([
                    "Time management", "Organization", "Study habits",
                    "Reading comprehension", "Mathematical concepts",
                    "Writing mechanics", "Participation", "Focus"
                ], k=random.randint(1, 3)),
                "learningStyle": random.choice(self.learning_styles)
            },
            "behavioralProfile": {
                "participation": {
                    "level": random.choice(self.participation_levels),
                    "notes": random.choice(self.teacher_notes_templates),
                    "lastUpdated": datetime.now().isoformat()
                },
                "socialSkills": {
                    "peerInteraction": random.choice(self.skill_levels),
                    "teamwork": random.choice(self.skill_levels),
                    "leadership": random.choice(self.skill_levels),
                    "notes": "Generally positive social interactions with peers"
                },
                "disciplineRecord": {
                    "incidents": random.randint(0, 3),
                    "lastIncident": (datetime.now() - timedelta(days=random.randint(10, 60))).isoformat(),
                    "positiveRecognitions": random.randint(1, 8),
                    "notes": "Overall positive behavioral record"
                },
                "attendance": {
                    "totalDays": 180,
                    "presentDays": random.randint(160, 180),
                    "tardyCount": random.randint(0, 10),
                    "attendanceRate": 0.0  # Will be calculated
                }
            },
            "extracurricular": {
                "sports": random.sample(self.extracurricular_sports, k=random.randint(0, 2)),
                "clubs": random.sample(self.extracurricular_clubs, k=random.randint(0, 3)),
                "competitions": [f"Competition {i+1}" for i in range(random.randint(0, 2))],
                "achievements": [f"Achievement {i+1}" for i in range(random.randint(0, 3))],
                "volunteerHours": random.randint(0, 40)
            },
            "parentEngagement": {
                "communicationFrequency": random.choice(["high", "medium", "low"]),
                "lastMeetingDate": (datetime.now() - timedelta(days=random.randint(30, 90))).isoformat(),
                "homeworkSupport": random.choice(self.skill_levels),
                "concernsRaised": random.sample([
                    "Academic performance", "Social development", "Homework completion",
                    "Classroom behavior", "Extracurricular balance"
                ], k=random.randint(0, 2)),
                "goalsSetting": random.sample([
                    "Improve math grades", "Better time management", "Increase participation",
                    "Develop reading skills", "Build confidence"
                ], k=random.randint(1, 3))
            },
            "teacherNotes": {
                "generalObservations": random.choice(self.teacher_notes_templates),
                "motivationLevel": random.choice(["high", "medium", "low"]),
                "homeworkCompletion": random.choice(["consistent", "inconsistent", "poor"]),
                "classroomBehavior": "Generally positive and engaged student",
                "specialNeeds": random.choice(["None", "Reading support", "Math tutoring", "ESL support"]),
                "recommendedActions": random.sample([
                    "Continue current approach", "Provide additional practice",
                    "Increase parent communication", "Consider tutoring",
                    "Encourage participation", "Focus on organization skills"
                ], k=random.randint(1, 3))
            },
            "goals": {
                "shortTerm": random.sample([
                    "Complete homework on time", "Improve test scores",
                    "Participate more in class", "Organize materials better"
                ], k=random.randint(1, 3)),
                "longTerm": random.sample([
                    "Achieve honor roll", "Develop leadership skills",
                    "Prepare for middle school", "Build strong study habits"
                ], k=random.randint(1, 2)),
                "parentGoals": random.sample([
                    "Support homework routine", "Encourage reading at home",
                    "Limit screen time", "Promote social activities"
                ], k=random.randint(1, 2)),
                "teacherGoals": random.sample([
                    "Increase student engagement", "Improve academic performance",
                    "Develop social skills", "Build confidence"
                ], k=random.randint(1, 2))
            },
            "metadata": {
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "lastMeetingPrep": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "academicYear": "2024-2025",
                "teacherId": f"TEACH_{uuid.uuid4().hex[:6].upper()}"
            }
        }

        # Calculate attendance rate
        attendance = student["behavioralProfile"]["attendance"]
        attendance["attendanceRate"] = round(
            attendance["presentDays"] / attendance["totalDays"], 3)

        return student

    def generate_multiple_students(self, count: int = 10, grade: str = "5") -> List[Dict[str, Any]]:
        """Generate multiple student records"""
        students = []
        for i in range(count):
            student = self.generate_student(grade)
            students.append(student)
        return students

    def save_to_json(self, students: List[Dict[str, Any]], filename: str = "synthetic_students.json"):
        """Save generated data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(students, f, indent=2, ensure_ascii=False)
        print(f"Generated {len(students)} student records saved to {filename}")


def main():
    """Generate synthetic student data"""
    generator = StudentDataGenerator()

    # Generate students for different grades
    all_students = []

    # Generate 5 students each for grades 3, 4, and 5
    for grade in ["3", "4", "5"]:
        grade_students = generator.generate_multiple_students(
            count=5, grade=grade)
        all_students.extend(grade_students)

    # Save main student data
    generator.save_to_json(all_students, "synthetic_students.json")

    # Generate and save sub-collection data for first student as example
    if all_students:
        sample_student = all_students[0]
        student_id = sample_student["studentId"]

        # Generate assessments
        assessments = generator.generate_assessments(student_id, 15)
        generator.save_to_json(assessments, f"assessments_{student_id}.json")

        # Generate behavioral incidents
        incidents = generator.generate_behavioral_incidents(student_id, 8)
        generator.save_to_json(
            incidents, f"behavioral_incidents_{student_id}.json")

        # Generate parent communications
        communications = generator.generate_parent_communications(
            student_id, 6)
        generator.save_to_json(
            communications, f"parent_communications_{student_id}.json")

        print(
            f"\nSample sub-collection data generated for student: {student_id}")
        print(f"- Assessments: {len(assessments)} records")
        print(f"- Behavioral incidents: {len(incidents)} records")
        print(f"- Parent communications: {len(communications)} records")

    print(f"\nTotal students generated: {len(all_students)}")
    print("Data structure follows the Firestore schema design for optimal AI analysis.")


if __name__ == "__main__":
    main()
