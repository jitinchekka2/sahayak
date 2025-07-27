# Firestore Database Schema for Parent-Teacher Meeting System

## Collections Structure

### 1. `students` Collection
**Document ID**: `student_id` (auto-generated or custom)

```json
{
  "studentId": "string",
  "personalInfo": {
    "firstName": "string",
    "lastName": "string",
    "dateOfBirth": "timestamp",
    "grade": "string",
    "section": "string",
    "rollNumber": "string",
    "parentEmail": "string",
    "parentPhone": "string",
    "address": "string",
    "emergencyContact": "string"
  },
  "academicProfile": {
    "currentGPA": "number",
    "subjects": {
      "mathematics": {
        "currentGrade": "string",
        "averageScore": "number",
        "trend": "improving|declining|stable",
        "lastAssessmentDate": "timestamp"
      },
      "english": {
        "currentGrade": "string",
        "averageScore": "number",
        "trend": "improving|declining|stable",
        "lastAssessmentDate": "timestamp"
      },
      "science": {
        "currentGrade": "string",
        "averageScore": "number",
        "trend": "improving|declining|stable",
        "lastAssessmentDate": "timestamp"
      }
      // ... other subjects
    },
    "strengths": ["string"],
    "areasForImprovement": ["string"],
    "learningStyle": "visual|auditory|kinesthetic|mixed"
  },
  "behavioralProfile": {
    "participation": {
      "level": "high|medium|low",
      "notes": "string",
      "lastUpdated": "timestamp"
    },
    "socialSkills": {
      "peerInteraction": "excellent|good|needs_improvement",
      "teamwork": "excellent|good|needs_improvement",
      "leadership": "excellent|good|needs_improvement",
      "notes": "string"
    },
    "disciplineRecord": {
      "incidents": "number",
      "lastIncident": "timestamp",
      "positiveRecognitions": "number",
      "notes": "string"
    },
    "attendance": {
      "totalDays": "number",
      "presentDays": "number",
      "tardyCount": "number",
      "attendanceRate": "number"
    }
  },
  "extracurricular": {
    "sports": ["string"],
    "clubs": ["string"],
    "competitions": ["string"],
    "achievements": ["string"],
    "volunteerHours": "number"
  },
  "parentEngagement": {
    "communicationFrequency": "high|medium|low",
    "lastMeetingDate": "timestamp",
    "homeworkSupport": "excellent|good|needs_improvement",
    "concernsRaised": ["string"],
    "goalsSetting": ["string"]
  },
  "teacherNotes": {
    "generalObservations": "string",
    "motivationLevel": "high|medium|low",
    "homeworkCompletion": "consistent|inconsistent|poor",
    "classroomBehavior": "string",
    "specialNeeds": "string",
    "recommendedActions": ["string"]
  },
  "goals": {
    "shortTerm": ["string"],
    "longTerm": ["string"],
    "parentGoals": ["string"],
    "teacherGoals": ["string"]
  },
  "metadata": {
    "createdAt": "timestamp",
    "updatedAt": "timestamp",
    "lastMeetingPrep": "timestamp",
    "academicYear": "string",
    "teacherId": "string"
  }
}
```

### 2. `assessments` Sub-collection (under each student)
**Path**: `students/{studentId}/assessments/{assessmentId}`

```json
{
  "assessmentId": "string",
  "subject": "string",
  "type": "quiz|test|project|assignment|exam",
  "date": "timestamp",
  "score": "number",
  "maxScore": "number",
  "percentage": "number",
  "topics": ["string"],
  "teacherFeedback": "string",
  "timeSpent": "number", // in minutes
  "difficulty": "easy|medium|hard",
  "mistakes": ["string"],
  "strengths": ["string"]
}
```

### 3. `behavioral_incidents` Sub-collection
**Path**: `students/{studentId}/behavioral_incidents/{incidentId}`

```json
{
  "incidentId": "string",
  "date": "timestamp",
  "type": "positive|negative",
  "category": "participation|discipline|leadership|helping_others|disruption|tardiness",
  "description": "string",
  "severity": "low|medium|high",
  "actionTaken": "string",
  "followUpRequired": "boolean",
  "teacherId": "string"
}
```

### 4. `parent_communications` Sub-collection
**Path**: `students/{studentId}/parent_communications/{communicationId}`

```json
{
  "communicationId": "string",
  "date": "timestamp",
  "type": "email|phone|meeting|note",
  "initiatedBy": "teacher|parent",
  "subject": "string",
  "content": "string",
  "followUpNeeded": "boolean",
  "followUpDate": "timestamp",
  "teacherId": "string"
}
```

## Benefits of This Schema

1. **Comprehensive Data**: Covers academic, behavioral, social, and personal aspects
2. **Temporal Tracking**: Timestamps allow tracking progress over time
3. **Structured Insights**: Easy to query for specific talking points
4. **Relationship Mapping**: Sub-collections maintain data relationships
5. **Scalable**: Can easily add new fields or collections
6. **AI-Friendly**: Structured format perfect for AI analysis

## Query Examples for AI Processing

1. **Academic Trends**: Get all assessments for trend analysis
2. **Behavioral Patterns**: Analyze behavioral incidents over time
3. **Parent Engagement**: Track communication frequency and content
4. **Goal Tracking**: Monitor progress towards set goals
5. **Comparative Analysis**: Compare performance across subjects

## AI Talking Points Generation

The AI can use this data to generate personalized talking points like:
- "Johnny has shown a 15% improvement in mathematics over the last quarter"
- "Sarah's participation in class discussions has increased significantly"
- "Mike might benefit from additional support in reading comprehension"
- "Emma's leadership skills are evident in her group project contributions"
