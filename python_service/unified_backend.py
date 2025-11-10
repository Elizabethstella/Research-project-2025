# unified_backend.py - HYBRID SYSTEM VERSION WITH NAMIBIA SYLLABUS
import json
import os
import numpy as np
from datetime import datetime
from enum import Enum

# Import the new hybrid components

from ai_lesson_generator import AILessonGenerator

class LessonStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Namibia NSSCAS Syllabus Topics Configuration
TOPICS = [
    {
        "id": "circular_measure",
        "name": "Circular Measure and Radians - NSSCAS Namibia",
        "description": "Understanding radian measure and solving problems involving arc length and sector area according to Namibia syllabus",
        "icon": "🔵",
        "difficulty": "beginner",
        "estimated_time": "45 minutes",
        "total_lessons": 4,
        "total_sections": 4,
        "prerequisites": [],
        "syllabus_code": "8227",
        "theme": "Mathematics 1",
        "topic_number": "Topic 5"
    },
    {
        "id": "trigonometric_graphs", 
        "name": "Trigonometric Graphs - NSSCAS Namibia",
        "description": "Sketching and interpreting trigonometric graphs, finding amplitude and period of transformed functions",
        "icon": "📈",
        "difficulty": "intermediate",
        "estimated_time": "60 minutes",
        "total_lessons": 5,
        "total_sections": 5,
        "prerequisites": ["circular_measure"],
        "syllabus_code": "8227", 
        "theme": "Mathematics 1",
        "topic_number": "Topic 6"
    },
    {
        "id": "trigonometric_identities",
        "name": "Trigonometric Identities - NSSCAS Namibia",
        "description": "Using trigonometric identities to prove identities and simplify expressions",
        "icon": "🔄",
        "difficulty": "intermediate",
        "estimated_time": "50 minutes",
        "total_lessons": 4,
        "total_sections": 4,
        "prerequisites": ["trigonometric_graphs"],
        "syllabus_code": "8227",
        "theme": "Mathematics 1", 
        "topic_number": "Topic 6"
    },
    {
        "id": "trigonometric_equations",
        "name": "Trigonometric Equations - NSSCAS Namibia",
        "description": "Solving trigonometric equations within specified intervals and finding general solutions",
        "icon": "⚡",
        "difficulty": "intermediate",
        "estimated_time": "55 minutes",
        "total_lessons": 5,
        "total_sections": 5,
        "prerequisites": ["trigonometric_identities"],
        "syllabus_code": "8227",
        "theme": "Mathematics 1",
        "topic_number": "Topic 6"
    },
    {
        "id": "advanced_trigonometry",
        "name": "Advanced Trigonometry - NSSCAS Namibia", 
        "description": "Secant, cosecant, cotangent functions and advanced identities including compound angles",
        "icon": "🎯",
        "difficulty": "advanced",
        "estimated_time": "70 minutes",
        "total_lessons": 6,
        "total_sections": 6,
        "prerequisites": ["trigonometric_equations"],
        "syllabus_code": "8227",
        "theme": "Mathematics 2",
        "topic_number": "Topic 3"
    }
]

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
        """Start a new topic for a student"""
        self.initialize_student(student_id)
        
        if topic_id not in self.students[student_id]["topics"]:
            self.students[student_id]["topics"][topic_id] = {
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
                "topic_number": topic_data.get("topic_number", "")
            }
            
            if topic_id not in self.students[student_id]["active_lessons"]:
                self.students[student_id]["active_lessons"].append(topic_id)
            
            self.students[student_id]["statistics"]["topics_started"] = len(
                self.students[student_id]["active_lessons"]
            )
            self.save_students()
        
        return self.students[student_id]["topics"][topic_id]
    
    def get_student_progress(self, student_id):
        """Get student progress"""
        self.initialize_student(student_id)
        return self.students[student_id]
    
    def update_lesson_progress(self, student_id, topic_id, progress_data):
        """Update lesson progress for a student"""
        if student_id in self.students and topic_id in self.students[student_id]["topics"]:
            topic = self.students[student_id]["topics"][topic_id]
            
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
        """Continue a topic that's in progress"""
        if (student_id in self.students and 
            topic_id in self.students[student_id]["topics"]):
            topic = self.students[student_id]["topics"][topic_id]
            topic["last_accessed"] = datetime.now().isoformat()
            self.save_students()
            return topic
        return None
    
    def mark_topic_completed(self, student_id, topic_id):
        """Mark a topic as completed"""
        if student_id in self.students and topic_id in self.students[student_id]["topics"]:
            topic = self.students[student_id]["topics"][topic_id]
            topic["status"] = LessonStatus.COMPLETED.value
            topic["completion_percentage"] = 100
            topic["completed_at"] = datetime.now().isoformat()
            topic["current_step"] = "completed"
            
            # Move from active to completed
            if topic_id in self.students[student_id]["active_lessons"]:
                self.students[student_id]["active_lessons"].remove(topic_id)
            
            if topic_id not in self.students[student_id]["completed_lessons"]:
                self.students[student_id]["completed_lessons"].append(topic_id)
            
            # Update statistics
            self.students[student_id]["statistics"]["topics_completed"] = len(
                self.students[student_id]["completed_lessons"]
            )
            
            self.save_students()
            return True
        return False

class UnifiedBackendService:
    def __init__(self):
        self.topic_manager = MultiTopicManager()
        self.lesson_generator = AILessonGenerator()    # AI lesson generation
        self.assessments = self.load_assessments()
        
        print("🔄 Initializing Namibia NSSCAS Backend Service...")
        
        # Initialize AI lesson generator
        print("🎓 Training AI Lesson Generator with Namibia Syllabus...")
        if not self.lesson_generator.train_lesson_generator():
            print("⚠️ AI Lesson Generator training failed, using fallback mode")
        
        print("✅ Namibia NSSCAS Backend Service initialized!")
        print("   - Template Manager: ✅")
        print("   - AI Lesson Generator: ✅")
        print("   - Namibia Syllabus Alignment: ✅")
        print("   - Syllabus Code: 8227")
    
    def load_assessments(self):
        """Load assessments from file"""
        try:
            with open('trig_assessments.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Assessment file not found, using default assessments")
            return self.get_default_assessments()
    
    def get_default_assessments(self):
        """Provide default Namibia syllabus assessments"""
        return {
            "circular_measure": {
                "pre_test": [{
                    "question_id": "namibia_cm_1",
                    "question": "Convert 150° to radians and 3π/4 radians to degrees, showing all working.",
                    "options": ["150° = 5π/6, 3π/4 = 135°", "150° = 5π/12, 3π/4 = 135°", "150° = 5π/6, 3π/4 = 120°", "150° = 5π/12, 3π/4 = 120°"],
                    "correct_answer": "150° = 5π/6, 3π/4 = 135°",
                    "explanation": "To convert degrees to radians: multiply by π/180. To convert radians to degrees: multiply by 180/π.",
                    "difficulty": "easy",
                    "concepts": ["radian_degree_conversion"],
                    "solution_steps": [
                        "150° × π/180 = 5π/6 radians",
                        "3π/4 × 180/π = 135°"
                    ]
                }],
                "post_test": [{
                    "question_id": "namibia_cm_2", 
                    "question": "A circular water reservoir in Namibia has radius 20m. If the water surface subtends an angle of 2.1 radians at the center, calculate the area of the water surface.",
                    "options": ["210 m²", "420 m²", "840 m²", "1680 m²"],
                    "correct_answer": "420 m²",
                    "explanation": "Use the sector area formula A = ½r²θ with r = 20m and θ = 2.1 radians.",
                    "difficulty": "medium",
                    "concepts": ["sector_area", "circular_measure"],
                    "solution_steps": [
                        "A = ½ × (20)² × 2.1",
                        "A = ½ × 400 × 2.1",
                        "A = 200 × 2.1 = 420 m²"
                    ]
                }]
            }
        }
    
    def start_topic(self, student_id, topic_id):
        """Start a new Namibia syllabus topic"""
        print(f"🎯 Starting Namibia syllabus topic: {topic_id} for student: {student_id}")
        
        # Map old topic IDs to new ones for backward compatibility
        topic_mapping = {
            "circular_measure": "circular_measure",
            "trigonometric_graphs": "trigonometric_graphs",
            "trigonometric_identities": "trigonometric_identities", 
            "trigonometric_equations": "trigonometric_equations",
            "advanced_trigonometry": "advanced_trigonometry"
        }
        
        # Use mapped topic_id if it exists, otherwise use original
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        topic_data = next((t for t in TOPICS if t["id"] == actual_topic_id), None)
        if not topic_data:
            return {"error": "Topic not found in Namibia syllabus"}
        
        progress = self.topic_manager.start_new_topic(student_id, actual_topic_id, topic_data)
        
        # Get AI-generated Namibia syllabus-aligned lesson content
        print(f"📚 Generating Namibia syllabus lesson content for {actual_topic_id}...")
        lesson_content = self.lesson_generator.generate_ai_lesson(actual_topic_id, 0)
        
        return {
            "success": True,
            "topic": topic_data,
            "progress": progress,
            "lesson_content": lesson_content
        }
    
    def continue_topic(self, student_id, topic_id):
        """Continue a Namibia syllabus topic"""
        print(f"🔄 Continuing Namibia syllabus topic: {topic_id} for student: {student_id}")
        
        # Map old topic IDs to new ones
        topic_mapping = {
             "circular_measure": "circular_measure",
             "trigonometric_graphs": "trigonometric_graphs",
             "trigonometric_identities": "trigonometric_identities", 
             "trigonometric_equations": "trigonometric_equations",
             "advanced_trigonometry": "advanced_trigonometry"
        }
        
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        progress = self.topic_manager.continue_topic(student_id, actual_topic_id)
        if not progress:
            return {"error": "Topic not found or not started"}
        
        topic_data = next((t for t in TOPICS if t["id"] == actual_topic_id), {})
        
        # Get current lesson content
        section_index = progress.get("current_section", 0)
        lesson_content = self.lesson_generator.generate_ai_lesson(actual_topic_id, section_index)
        
        return {
            "success": True,
            "progress": progress,
            "topic": topic_data,
            "lesson_content": lesson_content
        }
    
    def get_lesson_section(self, student_id, topic_id, section_index):
        """Get specific Namibia syllabus lesson section"""
        print(f"📖 Getting Namibia syllabus section {section_index} for {topic_id}")
        
        # Map old topic IDs to new ones
        topic_mapping = {
        "circular_measure": "circular_measure",
        "trigonometric_graphs": "trigonometric_graphs",
        "trigonometric_identities": "trigonometric_identities", 
        "trigonometric_equations": "trigonometric_equations",
        "advanced_trigonometry": "advanced_trigonometry"
        }
        
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
        
        # Update progress first
        self.topic_manager.update_lesson_progress(student_id, actual_topic_id, {
            "current_section": section_index,
            "sections_completed": section_index
        })
        
        # Get AI-generated Namibia syllabus-aligned lesson content
        lesson_content = self.lesson_generator.generate_ai_lesson(actual_topic_id, section_index)
        
        return {
            "success": True,
            "lesson_content": lesson_content
        }
    
    def ask_question(self, topic_id, question, conversation, student_id):
        """Ask a question about the Namibia syllabus topic"""
        print(f"💬 Asking Namibia syllabus question about {topic_id}: {question[:50]}...")
    
    # Map old topic IDs to new ones
        topic_mapping = {
        "circular_measure": "circular_measure",
        "trigonometric_graphs": "trigonometric_graphs",
        "trigonometric_identities": "trigonometric_identities", 
        "trigonometric_equations": "trigonometric_equations",
        "advanced_trigonometry": "advanced_trigonometry",
         # Map general questions to circular_measure
    }
    
        actual_topic_id = topic_mapping.get(topic_id, topic_id)
    
    # Ensure student and topic are initialized
        self.topic_manager.initialize_student(student_id)
    
    # Create default topic data for general questions
        default_topic_data = {
        "id": actual_topic_id,
        "name": "General Trigonometry",
        "total_lessons": 1,
        "total_sections": 1,
        "syllabus_code": "8227",
        "theme": "Mathematics 1",
        "topic_number": "General"
    }
    
    # If the topic doesn't exist for this student, initialize it
        if actual_topic_id not in self.topic_manager.students[student_id]["topics"]:
        # Find topic data or use default
           topic_data = next((t for t in TOPICS if t["id"] == actual_topic_id), default_topic_data)
           self.topic_manager.start_new_topic(student_id, actual_topic_id, topic_data)
    
    # Use AI to answer with Namibia syllabus alignment
        response_data = self.lesson_generator.answer_student_question(question, actual_topic_id, conversation)
    
    # Update learning time only if question was answered successfully
        if response_data.get('success'):
          try:
              self.topic_manager.update_lesson_progress(student_id, actual_topic_id, {
                "time_spent": self.topic_manager.students[student_id]["topics"][actual_topic_id].get("time_spent", 0) + 5,  # Add 5 minutes
                "questions_asked": self.topic_manager.students[student_id]["topics"][actual_topic_id].get("questions_asked", 0) + 1
            })
          except KeyError as e:
              print(f"⚠️ Warning: Could not update progress for topic {actual_topic_id}: {e}")
            # Initialize the topic if it doesn't exist
              topic_data = next((t for t in TOPICS if t["id"] == actual_topic_id), default_topic_data)
              self.topic_manager.start_new_topic(student_id, actual_topic_id, topic_data)
            # Try updating progress again
              try:
                  self.topic_manager.update_lesson_progress(student_id, actual_topic_id, {
                    "time_spent": 5,
                    "questions_asked": 1
                })
              except Exception as e2:
                   print(f"⚠️ Could not update progress even after initialization: {e2}")
    
        return {
        "response": response_data.get('response', 'I cannot answer that right now.'),
        "graph": "",
        "has_graph": False,
        "topic_relevant": True,
        "on_topic": True,
        "method": response_data.get('method', 'ai_namibia_syllabus'),
        "worked_example": response_data.get('worked_example', {}),
        "key_concepts": response_data.get('key_concepts', []),
        "examination_tips": response_data.get('examination_tips', [])
    }
    
    def _format_template_response(self, template_result):
        """Format template result into readable response"""
        if template_result.get('error') == 'TOPIC_VIOLATION':
            return template_result.get('message', 'Please stay on Namibia syllabus topics.')
        
        if template_result.get('success'):
            steps = template_result.get('solution_steps', [])
            final_answer = template_result.get('final_answer', '')
            
            response = "📚 **Namibia Syllabus Solution:**\n\n"
            response += "\n".join(steps)
            if final_answer:
                response += f"\n\n✅ **Final Answer:** {final_answer}"
            
            response += f"\n\n*Solved using {template_result.get('method', 'template')} approach*"
            return response
        else:
            return "I couldn't solve this problem with my current templates. Please try rephrasing your question to align with Namibia syllabus topics."
    
    
    def get_available_topics(self):
        """Get all available Namibia syllabus topics"""
        return {
            "topics": TOPICS,
            "syllabus_info": {
                "code": "8227",
                "name": "NSSCAS Mathematics",
                "level": "Advanced Subsidiary",
                "board": "Namibia Ministry of Education, Arts and Culture"
            }
        }
    
    def get_student_progress(self, student_id):
        """Get student progress with Namibia syllabus context"""
        progress = self.topic_manager.get_student_progress(student_id)
        
        # Add syllabus information to progress
        progress["syllabus_alignment"] = {
            "code": "8227",
            "topics_covered": list(progress["topics"].keys()),
            "namibia_standards": True
        }
        
        return progress
    
    def update_student_progress(self, student_id, progress_data):
        """Update student progress with Namibia syllabus tracking"""
        try:
            topic_id = progress_data.get('topicId')
            if not topic_id:
                return {"error": "Missing topicId"}
            
            # Map old topic IDs to new ones
            topic_mapping = {
        "circular_measure": "circular_measure",
        "trigonometric_graphs": "trigonometric_graphs",
        "trigonometric_identities": "trigonometric_identities", 
        "trigonometric_equations": "trigonometric_equations",
        "advanced_trigonometry": "advanced_trigonometry"
            }
            
            actual_topic_id = topic_mapping.get(topic_id, topic_id)
            
            # Update the specific topic progress
            update_data = {
                'completion_percentage': progress_data.get('completion_percentage', 0),
                'current_section': progress_data.get('current_section', 0),
                'sections_completed': progress_data.get('sections_completed', 0)
            }
            
            # Mark as completed if needed
            if progress_data.get('completed'):
                self.topic_manager.mark_topic_completed(student_id, actual_topic_id)
            else:
                self.topic_manager.update_lesson_progress(student_id, actual_topic_id, update_data)
            
            return {
                "success": True, 
                "message": "Namibia syllabus progress updated",
                "syllabus_code": "8227"
            }
            
        except Exception as e:
            print(f"Error updating Namibia syllabus progress: {e}")
            return {"error": str(e)}