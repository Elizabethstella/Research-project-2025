import json
import os
from datetime import datetime
from enum import Enum

class LessonStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class MultiTopicManager:
    def __init__(self):
        self.students_file = "students_progress.json"
        self.students = self.load_students()
    
    def load_students(self):
        """Load student progress from file"""
        try:
            if os.path.exists(self.students_file):
                with open(self.students_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading students: {e}")
        return {}
    
    def save_students(self):
        """Save student progress to file"""
        try:
            with open(self.students_file, 'w') as f:
                json.dump(self.students, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving students: {e}")
            return False
    
    def initialize_student(self, student_id):
        """Initialize a new student"""
        if student_id not in self.students:
            self.students[student_id] = {
                "topics": {},
                "active_lessons": [],
                "completed_lessons": [],
                "statistics": {
                    "total_learning_time": 0,
                    "topics_started": 0,
                    "topics_completed": 0,
                    "average_improvement": 0
                },
                "last_activity": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
            self.save_students()
        return self.students[student_id]
    
    def start_new_topic(self, student_id, topic_id, topic_data):
        """Start a new topic for a student with Namibia syllabus support"""
        self.initialize_student(student_id)
        
        # Map old topic IDs to new Namibia syllabus IDs for backward compatibility
        topic_mapping = {
            "graph_transformations": "trigonometric_graphs",
            "trig_equations": "trigonometric_equations", 
            "trig_identities": "trigonometric_identities"
        }
        
        # Use mapped topic_id if it exists, otherwise use original
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        if actual_topic_id not in self.students[student_id]["topics"]:
            self.students[student_id]["topics"][actual_topic_id] = {
                "status": LessonStatus.IN_PROGRESS.value,
                "started_at": datetime.now().isoformat(),
                "current_lesson": 0,
                "current_section": 0,
                "total_lessons": topic_data.get("total_lessons", 1),
                "completion_percentage": 0,
                "pre_test_score": None,
                "post_test_score": None,
                "current_step": "pre_test",
                "lesson_progress": {},
                "time_spent": 0,
                "last_accessed": datetime.now().isoformat(),
                "sections_completed": 0,
                "total_sections": topic_data.get("total_sections", 4),
                "syllabus_code": topic_data.get("syllabus_code", "8227"),
                "theme": topic_data.get("theme", ""),
                "topic_number": topic_data.get("topic_number", ""),
                "original_topic_id": topic_id  # Store original for reference
            }
            
            if actual_topic_id not in self.students[student_id]["active_lessons"]:
                self.students[student_id]["active_lessons"].append(actual_topic_id)
            
            self.students[student_id]["statistics"]["topics_started"] = len(
                self.students[student_id]["active_lessons"]
            )
            self.save_students()
        
        return self.students[student_id]["topics"][actual_topic_id]
    
    def get_student_progress(self, student_id):
        """Get student progress"""
        self.initialize_student(student_id)
        return self.students[student_id]
    
    def update_lesson_progress(self, student_id, topic_id, progress_data):
        """Update lesson progress for a student with Namibia syllabus support"""
        # Map old topic IDs to new ones
        topic_mapping = {
            "graph_transformations": "trigonometric_graphs",
            "trig_equations": "trigonometric_equations",
            "trig_identities": "trigonometric_identities"
        }
        
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        if student_id in self.students and actual_topic_id in self.students[student_id]["topics"]:
            topic = self.students[student_id]["topics"][actual_topic_id]
            
            # Update progress data
            for key, value in progress_data.items():
                topic[key] = value
            
            topic["last_accessed"] = datetime.now().isoformat()
            
            # FIX: Proper completion percentage calculation
            current_section = progress_data.get("current_section", topic.get("current_section", 0))
            total_sections = topic.get("total_sections", 4)
            
            if total_sections > 0:
                completion = (current_section / total_sections) * 100
                topic["completion_percentage"] = min(round(completion, 2), 100)
                
                # Update current_section in topic
                topic["current_section"] = current_section
                
                # Update sections_completed
                if current_section > topic.get("sections_completed", 0):
                    topic["sections_completed"] = current_section
            
            self.save_students()
            return True
        return False
    
    def continue_topic(self, student_id, topic_id):
        """Continue a topic that's in progress with Namibia syllabus support"""
        # Map old topic IDs to new ones
        topic_mapping = {
            "graph_transformations": "trigonometric_graphs",
            "trig_equations": "trigonometric_equations",
            "trig_identities": "trigonometric_identities"
        }
        
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        if (student_id in self.students and 
            actual_topic_id in self.students[student_id]["topics"]):
            topic = self.students[student_id]["topics"][actual_topic_id]
            topic["last_accessed"] = datetime.now().isoformat()
            self.save_students()
            return topic
        return None
    
    def mark_topic_completed(self, student_id, topic_id):
        """Mark a topic as completed with Namibia syllabus support"""
        # Map old topic IDs to new ones
        topic_mapping = {
            "graph_transformations": "trigonometric_graphs",
            "trig_equations": "trigonometric_equations",
            "trig_identities": "trigonometric_identities"
        }
        
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        if student_id in self.students and actual_topic_id in self.students[student_id]["topics"]:
            topic = self.students[student_id]["topics"][actual_topic_id]
            topic["status"] = LessonStatus.COMPLETED.value
            topic["completion_percentage"] = 100
            topic["completed_at"] = datetime.now().isoformat()
            topic["current_step"] = "completed"
            
            # Move from active to completed
            if actual_topic_id in self.students[student_id]["active_lessons"]:
                self.students[student_id]["active_lessons"].remove(actual_topic_id)
            
            if actual_topic_id not in self.students[student_id]["completed_lessons"]:
                self.students[student_id]["completed_lessons"].append(actual_topic_id)
            
            # Update statistics
            self.students[student_id]["statistics"]["topics_completed"] = len(
                self.students[student_id]["completed_lessons"]
            )
            
            self.save_students()
            return True
        return False
    
    def get_topic_sections(self, topic_id):
        """Get sections for a topic with Namibia syllabus alignment"""
        # Map old topic IDs to new ones
        topic_mapping = {
            "graph_transformations": "trigonometric_graphs",
            "trig_equations": "trigonometric_equations",
            "trig_identities": "trigonometric_identities"
        }
        
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        section_map = {
            "circular_measure": [
                "Radian Definition and Conversion", 
                "Arc Length and Applications",
                "Sector Area and Practical Problems", 
                "Namibia Context Applications"
            ],
            "trigonometric_graphs": [
                "Basic Trigonometric Graphs", 
                "Amplitude and Period",
                "Graph Transformations", 
                "Inverse Trigonometric Functions",
                "Exact Values and Applications"
            ],
            "trigonometric_identities": [
                "Basic Trigonometric Identities", 
                "Pythagorean Identities",
                "Identity Proofs and Simplification", 
                "Advanced Identity Applications"
            ],
            "trigonometric_equations": [
                "Solving Basic Equations", 
                "Equations with Multiple Angles",
                "Using Identities in Equations", 
                "General Solutions",
                "Namibia Examination Practice"
            ],
            "advanced_trigonometry": [
                "Secant, Cosecant, Cotangent", 
                "Compound Angle Formulae",
                "Double Angle Formulae", 
                "R-form Expressions",
                "Advanced Equation Solving", 
                "Namibia Syllabus Mastery"
            ]
        }
        return section_map.get(actual_topic_id, [f"Section {i+1}" for i in range(4)])
    
    def get_student_topics_with_mapping(self, student_id):
        """Get student topics with both old and new IDs for compatibility"""
        self.initialize_student(student_id)
        student_data = self.students[student_id]
        
        # Create reverse mapping for frontend compatibility
        reverse_mapping = {
            "trigonometric_graphs": "graph_transformations",
            "trigonometric_equations": "trig_equations", 
            "trigonometric_identities": "trig_identities"
        }
        
        mapped_topics = {}
        for topic_id, topic_data in student_data.get("topics", {}).items():
            # Use reverse mapping if exists, otherwise use original
            frontend_topic_id = reverse_mapping.get(topic_id, topic_id)
            mapped_topics[frontend_topic_id] = topic_data
            mapped_topics[frontend_topic_id]["actual_topic_id"] = topic_id
        
        return mapped_topics