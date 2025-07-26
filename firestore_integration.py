import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import os


class StudentDatabase:
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firestore connection

        Args:
            credentials_path: Path to Firebase service account key JSON file
                            If None, uses GOOGLE_APPLICATION_CREDENTIALS env var
        """
        if not firebase_admin._apps:
            if credentials_path:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials from environment
                firebase_admin.initialize_app()

        self.db = firestore.client()
        self.students_collection = "students"

    def add_student(self, student_data: Dict[str, Any]) -> str:
        """
        Add a new student to the database

        Args:
            student_data: Complete student data dictionary

        Returns:
            Document ID of the created student
        """
        try:
            doc_ref = self.db.collection(self.students_collection).document()
            student_data['metadata']['createdAt'] = datetime.now()
            student_data['metadata']['updatedAt'] = datetime.now()

            doc_ref.set(student_data)
            print(f"Student added with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error adding student: {e}")
            raise

    def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a student's complete data

        Args:
            student_id: Firestore document ID of the student

        Returns:
            Student data dictionary or None if not found
        """
        try:
            doc_ref = self.db.collection(
                self.students_collection).document(student_id)
            doc = doc_ref.get()

            if doc.exists:
                return doc.to_dict()
            else:
                print(f"Student with ID {student_id} not found")
                return None
        except Exception as e:
            print(f"Error retrieving student: {e}")
            raise

    def update_student(self, student_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update student data

        Args:
            student_id: Firestore document ID of the student
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = self.db.collection(
                self.students_collection).document(student_id)
            updates['metadata.updatedAt'] = datetime.now()

            doc_ref.update(updates)
            print(f"Student {student_id} updated successfully")
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False

    def get_students_by_grade(self, grade: str) -> List[Dict[str, Any]]:
        """
        Get all students in a specific grade

        Args:
            grade: Grade level (e.g., "5", "6")

        Returns:
            List of student data dictionaries
        """
        try:
            students_ref = self.db.collection(self.students_collection)
            query = students_ref.where("personalInfo.grade", "==", grade)
            docs = query.stream()

            students = []
            for doc in docs:
                student_data = doc.to_dict()
                student_data['firestore_id'] = doc.id
                students.append(student_data)

            return students
        except Exception as e:
            print(f"Error retrieving students by grade: {e}")
            raise

    def get_students_by_teacher(self, teacher_id: str) -> List[Dict[str, Any]]:
        """
        Get all students assigned to a specific teacher

        Args:
            teacher_id: Teacher's unique identifier

        Returns:
            List of student data dictionaries
        """
        try:
            students_ref = self.db.collection(self.students_collection)
            query = students_ref.where("metadata.teacherId", "==", teacher_id)
            docs = query.stream()

            students = []
            for doc in docs:
                student_data = doc.to_dict()
                student_data['firestore_id'] = doc.id
                students.append(student_data)

            return students
        except Exception as e:
            print(f"Error retrieving students by teacher: {e}")
            raise

    def add_assessment(self, student_id: str, assessment_data: Dict[str, Any]) -> str:
        """
        Add an assessment record to a student's sub-collection

        Args:
            student_id: Firestore document ID of the student
            assessment_data: Assessment data dictionary

        Returns:
            Document ID of the created assessment
        """
        try:
            assessments_ref = self.db.collection(self.students_collection).document(
                student_id).collection("assessments")
            doc_ref = assessments_ref.document()

            assessment_data['date'] = datetime.fromisoformat(
                assessment_data['date'].replace('Z', '+00:00'))
            doc_ref.set(assessment_data)

            print(f"Assessment added for student {student_id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error adding assessment: {e}")
            raise

    def get_student_assessments(self, student_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all assessments for a student

        Args:
            student_id: Firestore document ID of the student
            limit: Maximum number of assessments to return

        Returns:
            List of assessment data dictionaries
        """
        try:
            assessments_ref = self.db.collection(self.students_collection).document(
                student_id).collection("assessments")
            query = assessments_ref.order_by("date", direction="DESCENDING")

            if limit:
                query = query.limit(limit)

            docs = query.stream()

            assessments = []
            for doc in docs:
                assessment_data = doc.to_dict()
                assessment_data['firestore_id'] = doc.id
                assessments.append(assessment_data)

            return assessments
        except Exception as e:
            print(f"Error retrieving assessments: {e}")
            raise

    def add_behavioral_incident(self, student_id: str, incident_data: Dict[str, Any]) -> str:
        """
        Add a behavioral incident record

        Args:
            student_id: Firestore document ID of the student
            incident_data: Incident data dictionary

        Returns:
            Document ID of the created incident
        """
        try:
            incidents_ref = self.db.collection(self.students_collection).document(
                student_id).collection("behavioral_incidents")
            doc_ref = incidents_ref.document()

            incident_data['date'] = datetime.fromisoformat(
                incident_data['date'].replace('Z', '+00:00'))
            doc_ref.set(incident_data)

            print(f"Behavioral incident added for student {student_id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error adding behavioral incident: {e}")
            raise

    def get_student_behavioral_incidents(self, student_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get behavioral incidents for a student

        Args:
            student_id: Firestore document ID of the student
            limit: Maximum number of incidents to return

        Returns:
            List of incident data dictionaries
        """
        try:
            incidents_ref = self.db.collection(self.students_collection).document(
                student_id).collection("behavioral_incidents")
            query = incidents_ref.order_by("date", direction="DESCENDING")

            if limit:
                query = query.limit(limit)

            docs = query.stream()

            incidents = []
            for doc in docs:
                incident_data = doc.to_dict()
                incident_data['firestore_id'] = doc.id
                incidents.append(incident_data)

            return incidents
        except Exception as e:
            print(f"Error retrieving behavioral incidents: {e}")
            raise

    def add_parent_communication(self, student_id: str, communication_data: Dict[str, Any]) -> str:
        """
        Add a parent communication record

        Args:
            student_id: Firestore document ID of the student
            communication_data: Communication data dictionary

        Returns:
            Document ID of the created communication
        """
        try:
            communications_ref = self.db.collection(self.students_collection).document(
                student_id).collection("parent_communications")
            doc_ref = communications_ref.document()

            communication_data['date'] = datetime.fromisoformat(
                communication_data['date'].replace('Z', '+00:00'))
            if 'followUpDate' in communication_data:
                communication_data['followUpDate'] = datetime.fromisoformat(
                    communication_data['followUpDate'].replace('Z', '+00:00'))

            doc_ref.set(communication_data)

            print(f"Parent communication added for student {student_id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error adding parent communication: {e}")
            raise

    def get_student_communications(self, student_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get parent communications for a student

        Args:
            student_id: Firestore document ID of the student
            limit: Maximum number of communications to return

        Returns:
            List of communication data dictionaries
        """
        try:
            communications_ref = self.db.collection(self.students_collection).document(
                student_id).collection("parent_communications")
            query = communications_ref.order_by("date", direction="DESCENDING")

            if limit:
                query = query.limit(limit)

            docs = query.stream()

            communications = []
            for doc in docs:
                communication_data = doc.to_dict()
                communication_data['firestore_id'] = doc.id
                communications.append(communication_data)

            return communications
        except Exception as e:
            print(f"Error retrieving parent communications: {e}")
            raise

    def get_complete_student_profile(self, student_id: str) -> Dict[str, Any]:
        """
        Get complete student profile including all sub-collections

        Args:
            student_id: Firestore document ID of the student

        Returns:
            Complete student profile with all related data
        """
        try:
            # Get main student data
            student_data = self.get_student(student_id)
            if not student_data:
                return {}

            # Get sub-collection data
            student_data['assessments'] = self.get_student_assessments(
                student_id)
            student_data['behavioral_incidents'] = self.get_student_behavioral_incidents(
                student_id)
            student_data['parent_communications'] = self.get_student_communications(
                student_id)

            return student_data
        except Exception as e:
            print(f"Error retrieving complete student profile: {e}")
            raise

    def bulk_import_students(self, students_data: List[Dict[str, Any]]) -> List[str]:
        """
        Import multiple students at once

        Args:
            students_data: List of student data dictionaries

        Returns:
            List of document IDs of created students
        """
        try:
            doc_ids = []
            batch = self.db.batch()

            for student_data in students_data:
                doc_ref = self.db.collection(
                    self.students_collection).document()
                student_data['metadata']['createdAt'] = datetime.now()
                student_data['metadata']['updatedAt'] = datetime.now()

                batch.set(doc_ref, student_data)
                doc_ids.append(doc_ref.id)

            batch.commit()
            print(f"Successfully imported {len(students_data)} students")
            return doc_ids
        except Exception as e:
            print(f"Error during bulk import: {e}")
            raise

    def search_students(self, field_path: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """
        Search students based on a field condition

        Args:
            field_path: Dot-separated field path (e.g., "academicProfile.currentGPA")
            operator: Firestore operator ("==", "!=", "<", "<=", ">", ">=", "in", "not-in")
            value: Value to compare against

        Returns:
            List of matching student data dictionaries
        """
        try:
            students_ref = self.db.collection(self.students_collection)
            query = students_ref.where(field_path, operator, value)
            docs = query.stream()

            students = []
            for doc in docs:
                student_data = doc.to_dict()
                student_data['firestore_id'] = doc.id
                students.append(student_data)

            return students
        except Exception as e:
            print(f"Error searching students: {e}")
            raise


def load_and_import_synthetic_data(db: StudentDatabase, json_file_path: str):
    """
    Load synthetic data from JSON file and import to Firestore

    Args:
        db: StudentDatabase instance
        json_file_path: Path to JSON file containing student data
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            students_data = json.load(f)

        print(f"Loading {len(students_data)} students from {json_file_path}")
        doc_ids = db.bulk_import_students(students_data)

        print(f"Successfully imported {len(doc_ids)} students to Firestore")
        return doc_ids
    except Exception as e:
        print(f"Error loading and importing data: {e}")
        raise


# Example usage
if __name__ == "__main__":
    # Initialize database (make sure to set GOOGLE_APPLICATION_CREDENTIALS)
    db = StudentDatabase()

    # Example: Load synthetic data
    # doc_ids = load_and_import_synthetic_data(db, "synthetic_students.json")

    # Example: Get students by grade
    # grade_5_students = db.get_students_by_grade("5")
    # print(f"Found {len(grade_5_students)} students in grade 5")

    # Example: Get complete profile for a student
    # if doc_ids:
    #     complete_profile = db.get_complete_student_profile(doc_ids[0])
    #     print(f"Complete profile retrieved for: {complete_profile['personalInfo']['firstName']}")

    print("Firestore database integration ready!")
