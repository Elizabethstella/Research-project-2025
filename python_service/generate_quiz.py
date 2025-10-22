import joblib
import os
import json
import random
import numpy as np
import time
from datetime import datetime

# Define paths
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "true_ai_tutor.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "trig_dataset.json")

# Load the AI tutor model for question matching
if os.path.exists(MODEL_PATH):
    ai_model = joblib.load(MODEL_PATH)
    print("✅ AI Tutor model loaded for quiz generation!")
else:
    ai_model = None
    print("⚠️ No AI model found for quiz generation")

# Load dataset
if os.path.exists(DATASET_PATH):
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
else:
    dataset = {}
    print("⚠️ No dataset found for quiz generation")

class QuizGenerator:
    def __init__(self):
        self.available_topics = self._extract_topics_from_dataset()
        self.active_quizzes = {}  # Store active quizzes with timers
    
    def _extract_topics_from_dataset(self):
        """Extract available topics from the dataset"""
        topics = set()
        
        # Extract from main categories
        for category in dataset.keys():
            if category != "metadata" and category != "lessons":
                topics.add(category)
        
        # Extract from questions
        if ai_model and 'categories' in ai_model:
            for category in ai_model['categories']:
                if category and category != "unknown":
                    topics.add(category)
        
        return sorted(list(topics))
    
    def get_available_topics(self):
        """Get list of available quiz topics"""
        return self.available_topics[:10]  # Return top 10 topics
    
    def get_popular_topics(self):
        """Get 3 most popular topics for the quiz generation page"""
        popular_topics = [
            "trigonometric identities",
            "solving trigonometric equations", 
            "graphing trigonometric functions"
        ]
        
        # Filter to only include topics we actually have
        available_popular = [topic for topic in popular_topics if topic in self.available_topics]
        
        # If we don't have the popular ones, use the first 3 available
        if len(available_popular) < 3:
            available_popular = self.available_topics[:3]
        
        return available_popular
    
    def _categorize_difficulty(self, question_data):
        """Categorize question difficulty and set time limits"""
        question_text = question_data.get('question', '').lower()
        
        # Simple difficulty detection with time limits
        if any(word in question_text for word in ['prove', 'verify', 'identity', 'complex']):
            return {'level': 'hard', 'time_limit': 300}  # 5 minutes
        elif any(word in question_text for word in ['solve', 'find', 'value', 'expression']):
            return {'level': 'medium', 'time_limit': 180}  # 3 minutes
        else:
            return {'level': 'easy', 'time_limit': 120}  # 2 minutes
    
    def _extract_final_answer(self, solution_steps):
        """Extract final answer from solution steps"""
        if not solution_steps:
            return "No answer available"
        
        # Look for the last step or a line that contains "answer", "final", "result"
        final_step = solution_steps[-1]
        
        # Try to extract just the answer part
        if "=" in final_step:
            parts = final_step.split("=")
            if len(parts) > 1:
                return parts[-1].strip()
        
        # If no clear answer format, return the last step
        return final_step
    
    def _get_questions_by_topic(self, topic):
        """Get all questions for a specific topic from the dataset"""
        questions = []
        
        # Method 1: Get from AI model categories
        if ai_model and 'categories' in ai_model and 'questions' in ai_model:
            for i, category in enumerate(ai_model['categories']):
                if topic.lower() in category.lower() and i < len(ai_model['questions']):
                    difficulty_info = self._categorize_difficulty({'question': ai_model['questions'][i]})
                    questions.append({
                        'question': ai_model['questions'][i],
                        'solution': ai_model['solutions'][i],
                        'alternative_solution': ai_model['alternative_solutions'][i] if i < len(ai_model['alternative_solutions']) else [],
                        'category': category,
                        'difficulty': difficulty_info['level'],
                        'time_limit': difficulty_info['time_limit'],
                        'final_answer': self._extract_final_answer(ai_model['solutions'][i])
                    })
        
        # Method 2: Get from dataset structure
        for category_name, items in dataset.items():
            if category_name != "metadata" and category_name != "lessons":
                if topic.lower() in category_name.lower():
                    for item in items:
                        if isinstance(item, dict) and "question" in item:
                            solution = item.get("step_by_step_solution", [])
                            difficulty_info = self._categorize_difficulty(item)
                            questions.append({
                                'question': item["question"],
                                'solution': solution,
                                'alternative_solution': item.get("alternative_solution", []),
                                'category': category_name,
                                'difficulty': difficulty_info['level'],
                                'time_limit': difficulty_info['time_limit'],
                                'final_answer': self._extract_final_answer(solution)
                            })
        
        return questions
    
    def generate_quiz(self, topic, num_questions=5, difficulty_mix=True):
        """Generate a quiz for a specific topic"""
        if topic not in self.available_topics:
            return {"error": f"Topic '{topic}' not available"}
        
        # Get all questions for the topic
        all_questions = self._get_questions_by_topic(topic)
        
        if not all_questions:
            return {"error": f"No questions found for topic: {topic}"}
        
        # Filter and select questions based on difficulty mix
        if difficulty_mix:
            easy_questions = [q for q in all_questions if q['difficulty'] == 'easy']
            medium_questions = [q for q in all_questions if q['difficulty'] == 'medium']
            hard_questions = [q for q in all_questions if q['difficulty'] == 'hard']
            
            # Distribute questions across difficulties
            selected_questions = []
            if easy_questions:
                selected_questions.extend(random.sample(easy_questions, min(2, len(easy_questions))))
            if medium_questions:
                selected_questions.extend(random.sample(medium_questions, min(2, len(medium_questions))))
            if hard_questions:
                selected_questions.extend(random.sample(hard_questions, min(1, len(hard_questions))))
            
            # If we need more questions, fill from available pool
            while len(selected_questions) < num_questions and all_questions:
                remaining = [q for q in all_questions if q not in selected_questions]
                if remaining:
                    selected_questions.append(random.choice(remaining))
                else:
                    break
        else:
            # Random selection without considering difficulty
            selected_questions = random.sample(all_questions, min(num_questions, len(all_questions)))
        
        # Create quiz ID and store with start time
        quiz_id = f"quiz_{int(time.time())}_{random.randint(1000, 9999)}"
        quiz_start_time = time.time()
        
        # Format quiz questions (without solutions initially)
        quiz_questions = []
        total_time = 0
        
        for i, q in enumerate(selected_questions):
            question_data = {
                'id': i + 1,
                'question': q['question'],
                'type': 'multiple_step',
                'difficulty': q['difficulty'],
                'category': q['category'],
                'time_limit': q['time_limit'],
                'time_limit_display': f"{q['time_limit'] // 60}:{q['time_limit'] % 60:02d} minutes",
                'hint': f"This is a {q['difficulty']} level question about {topic}",
                'answer_available_after': quiz_start_time + total_time + q['time_limit'],
                # Don't include solutions in initial response
            }
            quiz_questions.append(question_data)
            total_time += q['time_limit']
        
        # Store the full quiz data with solutions for later retrieval
        self.active_quizzes[quiz_id] = {
            'topic': topic,
            'start_time': quiz_start_time,
            'questions': selected_questions,  # Store with solutions
            'formatted_questions': quiz_questions,  # Store without solutions
            'total_duration': total_time
        }
        
        # Clean up old quizzes (older than 24 hours)
        self._cleanup_old_quizzes()
        
        return {
            "quiz_id": quiz_id,
            "topic": topic,
            "total_questions": len(quiz_questions),
            "difficulty_mix": difficulty_mix,
            "questions": quiz_questions,
            "total_duration": total_time,
            "total_duration_display": f"{total_time // 60}:{total_time % 60:02d} minutes",
            "instructions": "Solve each trigonometric problem. Answers will be revealed after the time limit for each question.",
            "note": "Use the get_question_answer endpoint to check if answers are available"
        }
    
    def get_question_answer(self, quiz_id, question_id):
        """Get answer for a specific question if time has passed"""
        if quiz_id not in self.active_quizzes:
            return {"error": "Quiz not found or expired"}
        
        quiz = self.active_quizzes[quiz_id]
        current_time = time.time()
        
        # Find the question
        question_data = None
        formatted_question = None
        
        for i, (q, fq) in enumerate(zip(quiz['questions'], quiz['formatted_questions'])):
            if fq['id'] == question_id:
                question_data = q
                formatted_question = fq
                break
        
        if not question_data:
            return {"error": "Question not found"}
        
        # Check if time has passed for this question
        if current_time >= formatted_question['answer_available_after']:
            return {
                "answer_available": True,
                "final_answer": question_data['final_answer'],
                "solution_steps": question_data['solution'],
                "alternative_solution": question_data['alternative_solution'],
                "time_remaining": 0,
                "message": "Answer is now available"
            }
        else:
            time_remaining = formatted_question['answer_available_after'] - current_time
            return {
                "answer_available": False,
                "time_remaining": int(time_remaining),
                "time_remaining_display": f"{int(time_remaining // 60)}:{int(time_remaining % 60):02d}",
                "message": f"Answer available in {int(time_remaining // 60)}:{int(time_remaining % 60):02d}"
            }
    
    def get_quiz_progress(self, quiz_id):
        """Get progress for entire quiz"""
        if quiz_id not in self.active_quizzes:
            return {"error": "Quiz not found or expired"}
        
        quiz = self.active_quizzes[quiz_id]
        current_time = time.time()
        
        progress = {
            "quiz_id": quiz_id,
            "topic": quiz['topic'],
            "total_questions": len(quiz['formatted_questions']),
            "current_time": current_time,
            "questions": []
        }
        
        for fq in quiz['formatted_questions']:
            time_remaining = max(0, fq['answer_available_after'] - current_time)
            progress['questions'].append({
                'question_id': fq['id'],
                'question_preview': fq['question'][:50] + "...",
                'difficulty': fq['difficulty'],
                'time_limit': fq['time_limit'],
                'answer_available': time_remaining == 0,
                'time_remaining': int(time_remaining),
                'time_remaining_display': f"{int(time_remaining // 60)}:{int(time_remaining % 60):02d}" if time_remaining > 0 else "Available"
            })
        
        return progress
    
    def _cleanup_old_quizzes(self):
        """Remove quizzes older than 24 hours"""
        current_time = time.time()
        expired_quizzes = []
        
        for quiz_id, quiz_data in self.active_quizzes.items():
            if current_time - quiz_data['start_time'] > 24 * 60 * 60:  # 24 hours
                expired_quizzes.append(quiz_id)
        
        for quiz_id in expired_quizzes:
            del self.active_quizzes[quiz_id]
    
    def get_quiz_statistics(self):
        """Get statistics about available quiz questions"""
        stats = {
            "total_topics": len(self.available_topics),
            "available_topics": self.available_topics,
            "popular_topics": self.get_popular_topics(),
            "active_quizzes": len(self.active_quizzes)
        }
        
        # Count questions per topic
        topic_counts = {}
        for topic in self.available_topics[:10]:  # Top 10 topics
            questions = self._get_questions_by_topic(topic)
            topic_counts[topic] = len(questions)
        
        stats["questions_per_topic"] = topic_counts
        
        return stats

# Create global instance
quiz_generator = QuizGenerator()

# API functions
def generate_quiz_for_topic(topic, num_questions=5):
    """Generate quiz for a specific topic"""
    return quiz_generator.generate_quiz(topic, num_questions)

def get_question_answer(quiz_id, question_id):
    """Get answer for a specific question"""
    return quiz_generator.get_question_answer(quiz_id, question_id)

def get_quiz_progress(quiz_id):
    """Get progress for a quiz"""
    return quiz_generator.get_quiz_progress(quiz_id)

def get_quiz_topics():
    """Get available quiz topics"""
    return quiz_generator.get_available_topics()

def get_popular_quiz_topics():
    """Get popular topics for quiz generation"""
    return quiz_generator.get_popular_topics()

def get_quiz_stats():
    """Get quiz statistics"""
    return quiz_generator.get_quiz_statistics()

# Test the quiz generator
if __name__ == "__main__":
    print("🧠 QUIZ GENERATOR TEST")
    print("=" * 50)
    
    stats = get_quiz_stats()
    print(f"📊 Available Topics: {stats['total_topics']}")
    print(f"🎯 Popular Topics: {', '.join(stats['popular_topics'])}")
    
    print(f"\n📝 Questions per topic:")
    for topic, count in stats['questions_per_topic'].items():
        print(f"   • {topic}: {count} questions")
    
    print(f"\n🔍 Testing Quiz Generation:")
    for topic in stats['popular_topics'][:1]:
        print(f"\n📚 Topic: '{topic}'")
        quiz = generate_quiz_for_topic(topic, 2)
        
        if "error" in quiz:
            print(f"   ❌ {quiz['error']}")
        else:
            print(f"   ✅ Generated {quiz['total_questions']} questions")
            print(f"   ⏱️  Total duration: {quiz['total_duration_display']}")
            print(f"   🆔 Quiz ID: {quiz['quiz_id']}")
            
            for q in quiz['questions']:
                print(f"      Q{q['id']} ({q['difficulty']}): {q['time_limit_display']}")
                print(f"         {q['question'][:60]}...")