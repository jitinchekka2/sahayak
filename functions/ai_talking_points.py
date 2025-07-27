"""
AI Talking Points Generator for Parent-Teacher Meetings
Analyzes student data and generates personalized talking points
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass


@dataclass
class TalkingPoint:
    category: str  # "academic", "behavioral", "social", "goals", "recommendations"
    priority: str  # "high", "medium", "low"
    title: str
    content: str
    supporting_data: Dict[str, Any]
    action_required: bool = False


class TalkingPointsGenerator:
    def __init__(self):
        self.grade_level_expectations = {
            "3": {"gpa_excellent": 3.5, "gpa_good": 3.0, "attendance_good": 0.95},
            "4": {"gpa_excellent": 3.6, "gpa_good": 3.1, "attendance_good": 0.95},
            "5": {"gpa_excellent": 3.7, "gpa_good": 3.2, "attendance_good": 0.96},
            "6": {"gpa_excellent": 3.8, "gpa_good": 3.3, "attendance_good": 0.96}
        }

    def analyze_academic_performance(self, student_data: Dict[str, Any]) -> List[TalkingPoint]:
        """Analyze academic performance and generate talking points"""
        talking_points = []
        academic_profile = student_data.get("academicProfile", {})
        grade = student_data.get("personalInfo", {}).get("grade", "5")
        expectations = self.grade_level_expectations.get(
            grade, self.grade_level_expectations["5"])

        # Overall GPA Analysis
        current_gpa = academic_profile.get("currentGPA", 0)
        if current_gpa >= expectations["gpa_excellent"]:
            talking_points.append(TalkingPoint(
                category="academic",
                priority="high",
                title="Excellent Academic Performance",
                content=f"{student_data['personalInfo']['firstName']} is performing exceptionally well with a GPA of {current_gpa:.2f}, which exceeds grade-level expectations.",
                supporting_data={"gpa": current_gpa,
                                 "expectation": expectations["gpa_excellent"]},
                action_required=False
            ))
        elif current_gpa >= expectations["gpa_good"]:
            talking_points.append(TalkingPoint(
                category="academic",
                priority="medium",
                title="Solid Academic Performance",
                content=f"{student_data['personalInfo']['firstName']} maintains good academic standing with a GPA of {current_gpa:.2f}.",
                supporting_data={"gpa": current_gpa,
                                 "expectation": expectations["gpa_good"]},
                action_required=False
            ))
        else:
            talking_points.append(TalkingPoint(
                category="academic",
                priority="high",
                title="Academic Support Needed",
                content=f"{student_data['personalInfo']['firstName']}'s GPA of {current_gpa:.2f} indicates need for additional academic support.",
                supporting_data={"gpa": current_gpa,
                                 "expectation": expectations["gpa_good"]},
                action_required=True
            ))

        # Subject-specific analysis
        subjects = academic_profile.get("subjects", {})
        for subject, data in subjects.items():
            trend = data.get("trend", "stable")
            score = data.get("averageScore", 0)
            grade_letter = data.get("currentGrade", "")

            if trend == "improving":
                talking_points.append(TalkingPoint(
                    category="academic",
                    priority="medium",
                    title=f"Improvement in {subject.title()}",
                    content=f"Great progress in {subject} with an improving trend. Current grade: {grade_letter} ({score:.1f}%)",
                    supporting_data={
                        "subject": subject, "trend": trend, "score": score, "grade": grade_letter}
                ))
            elif trend == "declining" and score < 75:
                talking_points.append(TalkingPoint(
                    category="academic",
                    priority="high",
                    title=f"Concerns in {subject.title()}",
                    content=f"{subject.title()} performance shows declining trend. Current grade: {grade_letter} ({score:.1f}%). Let's discuss intervention strategies.",
                    supporting_data={
                        "subject": subject, "trend": trend, "score": score, "grade": grade_letter},
                    action_required=True
                ))

        # Strengths and areas for improvement
        strengths = academic_profile.get("strengths", [])
        if strengths:
            talking_points.append(TalkingPoint(
                category="academic",
                priority="medium",
                title="Academic Strengths",
                content=f"{student_data['personalInfo']['firstName']} excels in: {', '.join(strengths)}. We can leverage these strengths in challenging areas.",
                supporting_data={"strengths": strengths}
            ))

        areas_for_improvement = academic_profile.get("areasForImprovement", [])
        if areas_for_improvement:
            talking_points.append(TalkingPoint(
                category="academic",
                priority="medium",
                title="Growth Opportunities",
                content=f"Areas where {student_data['personalInfo']['firstName']} can grow: {', '.join(areas_for_improvement)}",
                supporting_data={
                    "areas_for_improvement": areas_for_improvement},
                action_required=True
            ))

        return talking_points

    def analyze_behavioral_profile(self, student_data: Dict[str, Any]) -> List[TalkingPoint]:
        """Analyze behavioral aspects and generate talking points"""
        talking_points = []
        behavioral_profile = student_data.get("behavioralProfile", {})
        first_name = student_data['personalInfo']['firstName']

        # Participation analysis
        participation = behavioral_profile.get("participation", {})
        participation_level = participation.get("level", "medium")

        if participation_level == "high":
            talking_points.append(TalkingPoint(
                category="behavioral",
                priority="medium",
                title="Excellent Class Participation",
                content=f"{first_name} demonstrates excellent class participation and engagement.",
                supporting_data={"participation_level": participation_level}
            ))
        elif participation_level == "low":
            talking_points.append(TalkingPoint(
                category="behavioral",
                priority="medium",
                title="Encouraging Participation",
                content=f"We're working on encouraging {first_name} to participate more actively in class discussions.",
                supporting_data={"participation_level": participation_level},
                action_required=True
            ))

        # Social skills analysis
        social_skills = behavioral_profile.get("socialSkills", {})
        peer_interaction = social_skills.get("peerInteraction", "good")
        teamwork = social_skills.get("teamwork", "good")

        if peer_interaction == "excellent" and teamwork == "excellent":
            talking_points.append(TalkingPoint(
                category="social",
                priority="medium",
                title="Strong Social Skills",
                content=f"{first_name} demonstrates excellent peer interaction and teamwork abilities.",
                supporting_data={
                    "peer_interaction": peer_interaction, "teamwork": teamwork}
            ))
        elif peer_interaction == "needs_improvement" or teamwork == "needs_improvement":
            talking_points.append(TalkingPoint(
                category="social",
                priority="medium",
                title="Social Skills Development",
                content=f"We're focusing on developing {first_name}'s social interaction skills through group activities.",
                supporting_data={
                    "peer_interaction": peer_interaction, "teamwork": teamwork},
                action_required=True
            ))

        # Attendance analysis
        attendance = behavioral_profile.get("attendance", {})
        attendance_rate = attendance.get("attendanceRate", 0)
        tardy_count = attendance.get("tardyCount", 0)

        if attendance_rate >= 0.98:
            talking_points.append(TalkingPoint(
                category="behavioral",
                priority="low",
                title="Excellent Attendance",
                content=f"{first_name} has excellent attendance with {attendance_rate:.1%} attendance rate.",
                supporting_data={
                    "attendance_rate": attendance_rate, "tardy_count": tardy_count}
            ))
        elif attendance_rate < 0.90:
            talking_points.append(TalkingPoint(
                category="behavioral",
                priority="high",
                title="Attendance Concerns",
                content=f"Attendance needs attention: {attendance_rate:.1%} rate. Regular attendance is crucial for academic success.",
                supporting_data={
                    "attendance_rate": attendance_rate, "tardy_count": tardy_count},
                action_required=True
            ))

        if tardy_count > 5:
            talking_points.append(TalkingPoint(
                category="behavioral",
                priority="medium",
                title="Punctuality",
                content=f"{first_name} has been tardy {tardy_count} times. Let's work together on morning routines.",
                supporting_data={"tardy_count": tardy_count},
                action_required=True
            ))

        return talking_points

    def analyze_extracurricular_engagement(self, student_data: Dict[str, Any]) -> List[TalkingPoint]:
        """Analyze extracurricular activities and engagement"""
        talking_points = []
        extracurricular = student_data.get("extracurricular", {})
        first_name = student_data['personalInfo']['firstName']

        sports = extracurricular.get("sports", [])
        clubs = extracurricular.get("clubs", [])
        achievements = extracurricular.get("achievements", [])
        volunteer_hours = extracurricular.get("volunteerHours", 0)

        total_activities = len(sports) + len(clubs)

        if total_activities >= 3:
            talking_points.append(TalkingPoint(
                category="social",
                priority="medium",
                title="Well-Rounded Engagement",
                content=f"{first_name} is actively involved in {total_activities} extracurricular activities, showing great balance.",
                supporting_data={"sports": sports, "clubs": clubs,
                                 "total_activities": total_activities}
            ))
        elif total_activities == 0:
            talking_points.append(TalkingPoint(
                category="social",
                priority="low",
                title="Extracurricular Opportunities",
                content=f"Consider encouraging {first_name} to explore extracurricular activities to develop new interests and skills.",
                supporting_data={"total_activities": total_activities},
                action_required=False
            ))

        if achievements:
            talking_points.append(TalkingPoint(
                category="social",
                priority="medium",
                title="Recognition and Achievements",
                content=f"{first_name} has earned recognition: {', '.join(achievements)}",
                supporting_data={"achievements": achievements}
            ))

        if volunteer_hours > 10:
            talking_points.append(TalkingPoint(
                category="social",
                priority="medium",
                title="Community Service",
                content=f"{first_name} has contributed {volunteer_hours} volunteer hours, showing strong community engagement.",
                supporting_data={"volunteer_hours": volunteer_hours}
            ))

        return talking_points

    def analyze_parent_engagement(self, student_data: Dict[str, Any]) -> List[TalkingPoint]:
        """Analyze parent engagement and communication"""
        talking_points = []
        parent_engagement = student_data.get("parentEngagement", {})
        first_name = student_data['personalInfo']['firstName']

        communication_frequency = parent_engagement.get(
            "communicationFrequency", "medium")
        homework_support = parent_engagement.get("homeworkSupport", "good")
        concerns_raised = parent_engagement.get("concernsRaised", [])

        if communication_frequency == "high":
            talking_points.append(TalkingPoint(
                category="goals",
                priority="low",
                title="Strong Parent Partnership",
                content=f"Your consistent communication and involvement greatly supports {first_name}'s success.",
                supporting_data={
                    "communication_frequency": communication_frequency}
            ))
        elif communication_frequency == "low":
            talking_points.append(TalkingPoint(
                category="goals",
                priority="medium",
                title="Increasing Communication",
                content=f"More frequent communication between home and school would benefit {first_name}'s progress.",
                supporting_data={
                    "communication_frequency": communication_frequency},
                action_required=True
            ))

        if homework_support == "excellent":
            talking_points.append(TalkingPoint(
                category="goals",
                priority="low",
                title="Homework Support",
                content=f"Thank you for providing excellent homework support. It shows in {first_name}'s consistent work quality.",
                supporting_data={"homework_support": homework_support}
            ))
        elif homework_support == "needs_improvement":
            talking_points.append(TalkingPoint(
                category="goals",
                priority="medium",
                title="Homework Partnership",
                content=f"Let's discuss strategies for supporting {first_name}'s homework routine at home.",
                supporting_data={"homework_support": homework_support},
                action_required=True
            ))

        if concerns_raised:
            talking_points.append(TalkingPoint(
                category="goals",
                priority="high",
                title="Addressing Parent Concerns",
                content=f"Let's discuss your concerns about: {', '.join(concerns_raised)}",
                supporting_data={"concerns_raised": concerns_raised},
                action_required=True
            ))

        return talking_points

    def analyze_goals_and_progress(self, student_data: Dict[str, Any]) -> List[TalkingPoint]:
        """Analyze goals setting and progress tracking"""
        talking_points = []
        goals = student_data.get("goals", {})
        teacher_notes = student_data.get("teacherNotes", {})
        first_name = student_data['personalInfo']['firstName']

        short_term_goals = goals.get("shortTerm", [])
        long_term_goals = goals.get("longTerm", [])
        parent_goals = goals.get("parentGoals", [])
        recommended_actions = teacher_notes.get("recommendedActions", [])

        if short_term_goals:
            talking_points.append(TalkingPoint(
                category="goals",
                priority="high",
                title="Short-term Goals Progress",
                content=f"Let's review progress on {first_name}'s short-term goals: {', '.join(short_term_goals)}",
                supporting_data={"short_term_goals": short_term_goals},
                action_required=True
            ))

        if long_term_goals:
            talking_points.append(TalkingPoint(
                category="goals",
                priority="medium",
                title="Long-term Vision",
                content=f"Working towards long-term goals: {', '.join(long_term_goals)}",
                supporting_data={"long_term_goals": long_term_goals}
            ))

        if recommended_actions:
            talking_points.append(TalkingPoint(
                category="recommendations",
                priority="high",
                title="Action Plan",
                content=f"Recommended next steps for {first_name}: {', '.join(recommended_actions)}",
                supporting_data={"recommended_actions": recommended_actions},
                action_required=True
            ))

        motivation_level = teacher_notes.get("motivationLevel", "medium")
        if motivation_level == "low":
            talking_points.append(TalkingPoint(
                category="recommendations",
                priority="high",
                title="Motivation Strategies",
                content=f"Let's discuss strategies to increase {first_name}'s motivation and engagement in learning.",
                supporting_data={"motivation_level": motivation_level},
                action_required=True
            ))

        return talking_points

    def generate_talking_points(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive talking points for a student"""
        all_talking_points = []

        # Analyze different aspects
        all_talking_points.extend(
            self.analyze_academic_performance(student_data))
        all_talking_points.extend(
            self.analyze_behavioral_profile(student_data))
        all_talking_points.extend(
            self.analyze_extracurricular_engagement(student_data))
        all_talking_points.extend(self.analyze_parent_engagement(student_data))
        all_talking_points.extend(
            self.analyze_goals_and_progress(student_data))

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        all_talking_points.sort(
            key=lambda x: priority_order.get(x.priority, 3))

        # Group by category
        categorized_points = {
            "academic": [],
            "behavioral": [],
            "social": [],
            "goals": [],
            "recommendations": []
        }

        for point in all_talking_points:
            categorized_points[point.category].append({
                "priority": point.priority,
                "title": point.title,
                "content": point.content,
                "supporting_data": point.supporting_data,
                "action_required": point.action_required
            })

        # Generate meeting summary
        first_name = student_data['personalInfo']['firstName']
        last_name = student_data['personalInfo']['lastName']
        grade = student_data['personalInfo']['grade']

        high_priority_count = len(
            [p for p in all_talking_points if p.priority == "high"])
        action_required_count = len(
            [p for p in all_talking_points if p.action_required])

        meeting_summary = {
            "student_name": f"{first_name} {last_name}",
            "grade": grade,
            "meeting_date": datetime.now().strftime("%Y-%m-%d"),
            "total_talking_points": len(all_talking_points),
            "high_priority_items": high_priority_count,
            "action_items": action_required_count,
            "overall_recommendation": self._generate_overall_recommendation(student_data, all_talking_points)
        }

        return {
            "meeting_summary": meeting_summary,
            "talking_points_by_category": categorized_points,
            "action_items": [p for p in all_talking_points if p.action_required],
            "strengths_to_celebrate": [p for p in all_talking_points if p.priority == "medium" and not p.action_required],
            "student_data_summary": self._create_data_summary(student_data)
        }

    def _generate_overall_recommendation(self, student_data: Dict[str, Any], talking_points: List[TalkingPoint]) -> str:
        """Generate overall recommendation based on analysis"""
        first_name = student_data['personalInfo']['firstName']
        high_priority_issues = [
            p for p in talking_points if p.priority == "high" and p.action_required]
        academic_gpa = student_data.get(
            "academicProfile", {}).get("currentGPA", 0)

        if len(high_priority_issues) >= 3:
            return f"{first_name} would benefit from increased support and intervention in multiple areas. Let's create a comprehensive action plan."
        elif academic_gpa >= 3.5 and len(high_priority_issues) <= 1:
            return f"{first_name} is performing well overall. Continue current strategies while addressing minor areas for growth."
        elif len(high_priority_issues) == 0:
            return f"{first_name} is doing excellent work. Focus on maintaining current performance and exploring enrichment opportunities."
        else:
            return f"{first_name} shows good potential. Targeted support in key areas will help maximize success."

    def _create_data_summary(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of key student data points"""
        return {
            "current_gpa": student_data.get("academicProfile", {}).get("currentGPA", 0),
            "attendance_rate": student_data.get("behavioralProfile", {}).get("attendance", {}).get("attendanceRate", 0),
            "participation_level": student_data.get("behavioralProfile", {}).get("participation", {}).get("level", "unknown"),
            "extracurricular_count": len(student_data.get("extracurricular", {}).get("sports", [])) + len(student_data.get("extracurricular", {}).get("clubs", [])),
            "learning_style": student_data.get("academicProfile", {}).get("learningStyle", "unknown"),
            "communication_frequency": student_data.get("parentEngagement", {}).get("communicationFrequency", "unknown")
        }


def generate_meeting_agenda(talking_points_data: Dict[str, Any]) -> str:
    """Generate a formatted meeting agenda"""
    summary = talking_points_data["meeting_summary"]

    agenda = f"""
PARENT-TEACHER MEETING AGENDA
Student: {summary['student_name']} (Grade {summary['grade']})
Date: {summary['meeting_date']}

MEETING OVERVIEW:
• Total Discussion Points: {summary['total_talking_points']}
• High Priority Items: {summary['high_priority_items']}
• Action Items: {summary['action_items']}

AGENDA ITEMS:

1. ACADEMIC PERFORMANCE
"""

    for point in talking_points_data["talking_points_by_category"]["academic"]:
        priority_marker = "🔴" if point["priority"] == "high" else "🟡" if point["priority"] == "medium" else "🟢"
        action_marker = " ⚡" if point["action_required"] else ""
        agenda += f"   {priority_marker} {point['title']}{action_marker}\n"

    agenda += "\n2. BEHAVIORAL & SOCIAL DEVELOPMENT\n"

    for point in talking_points_data["talking_points_by_category"]["behavioral"] + talking_points_data["talking_points_by_category"]["social"]:
        priority_marker = "🔴" if point["priority"] == "high" else "🟡" if point["priority"] == "medium" else "🟢"
        action_marker = " ⚡" if point["action_required"] else ""
        agenda += f"   {priority_marker} {point['title']}{action_marker}\n"

    agenda += "\n3. GOALS & ACTION PLAN\n"

    for point in talking_points_data["talking_points_by_category"]["goals"] + talking_points_data["talking_points_by_category"]["recommendations"]:
        priority_marker = "🔴" if point["priority"] == "high" else "🟡" if point["priority"] == "medium" else "🟢"
        action_marker = " ⚡" if point["action_required"] else ""
        agenda += f"   {priority_marker} {point['title']}{action_marker}\n"

    agenda += f"\nOVERALL RECOMMENDATION:\n{summary['overall_recommendation']}\n"
    agenda += "\nLEGEND: 🔴 High Priority | 🟡 Medium Priority | 🟢 Low Priority | ⚡ Action Required"

    return agenda