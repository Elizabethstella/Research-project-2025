import json
import joblib
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

DATASET_PATH = os.path.join(os.path.dirname(__file__), "trig_dataset.json")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "true_ai_tutor.pkl")
LESSON_MODEL_PATH = os.path.join(os.path.dirname(__file__), "lesson_generator.pkl")

class LessonGenerator:
    """Dedicated model for lesson generation and teaching"""
    
    def __init__(self):
        self.dataset = None
        self.semantic_model = None
        self.lesson_embeddings = None
        self.lesson_topics = []
        self.lesson_content = []
        self.concept_explanations = []
        self.worked_examples = []
        self.practice_exercises = []
        self.lesson_metadata = []
        
    def load_dataset(self):
        """Load the trigonometric dataset"""
        try:
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print("❌ trig_dataset.json not found")
            return {}
    
    def extract_lessons_from_dataset(self):
        """Extract lessons data from the main dataset"""
        if not self.dataset:
            print("   ❌ No dataset loaded")
            return
        
        # Look for lessons in the dataset
        lessons_data = []
        
        # Check if lessons are in the main dataset structure
        if "lessons" in self.dataset:
            lessons_data = self.dataset["lessons"]
            print(f"   📚 Found {len(lessons_data)} lessons in main dataset")
        else:
            print("   ⚠️  No 'lessons' key found in dataset")
            return
        
        if not lessons_data:
            print("   ⚠️  No lessons found for training")
            return
        
        # Process each lesson
        for lesson in lessons_data:
            if not isinstance(lesson, dict):
                continue
                
            lesson_id = lesson.get('lesson_id', f"lesson_{len(self.lesson_metadata)}")
            topic = lesson.get('topic', 'Unknown Topic')
            title = lesson.get('title', 'Untitled Lesson')
            
            # Store lesson metadata
            self.lesson_metadata.append({
                'lesson_id': lesson_id,
                'topic': topic,
                'title': title,
                'syllabus_ref': lesson.get('syllabus_ref', ''),
                'learning_objectives': lesson.get('learning_objectives', [])
            })
            
            full_topic = f"{topic} - {title}"
            self.lesson_topics.append(full_topic)
            
            # Extract and structure concept explanations
            if "theory_explanation" in lesson:
                for explanation in lesson["theory_explanation"]:
                    self.concept_explanations.append({
                        'lesson_id': lesson_id,
                        'topic': full_topic,
                        'concept': explanation,
                        'type': 'theory',
                        'content': explanation
                    })
            
            # Extract learning objectives as concepts
            if "learning_objectives" in lesson:
                for objective in lesson["learning_objectives"]:
                    self.concept_explanations.append({
                        'lesson_id': lesson_id,
                        'topic': full_topic,
                        'concept': objective,
                        'type': 'learning_objective',
                        'content': objective
                    })
            
            # Extract key formulas and identities
            if "key_formulas" in lesson:
                for formula in lesson["key_formulas"]:
                    self.concept_explanations.append({
                        'lesson_id': lesson_id,
                        'topic': full_topic,
                        'concept': formula,
                        'type': 'formula',
                        'content': formula
                    })
            
            if "key_identities" in lesson:
                for identity in lesson["key_identities"]:
                    self.concept_explanations.append({
                        'lesson_id': lesson_id,
                        'topic': full_topic,
                        'concept': identity,
                        'type': 'identity',
                        'content': identity
                    })
            
            # Extract worked examples
            if "worked_examples" in lesson:
                for example in lesson["worked_examples"]:
                    self.worked_examples.append({
                        'lesson_id': lesson_id,
                        'topic': full_topic,
                        'example_id': example.get('example_id', ''),
                        'title': example.get('title', ''),
                        'question': example.get('question', ''),
                        'solution': example.get('step_by_step_solution', []),
                        'explanation': example.get('explanation', ''),
                        'difficulty': example.get('difficulty', 'Basic'),
                        'plotting_instructions': example.get('plotting_instructions', {}),
                        'matplotlib_code': example.get('matplotlib_code', '')
                    })
            
            # Extract practice exercises
            if "practice_exercises" in lesson:
                for exercise in lesson["practice_exercises"]:
                    self.practice_exercises.append({
                        'lesson_id': lesson_id,
                        'topic': full_topic,
                        'exercise_id': exercise.get('id', ''),
                        'question': exercise.get('question', ''),
                        'solution': exercise.get('step_by_step_solution', []),
                        'final_answer': exercise.get('final_answer', ''),
                        'difficulty': exercise.get('difficulty', 'Basic')
                    })
            
            # Combine all content for semantic search
            lesson_content = self._combine_lesson_content(lesson)
            self.lesson_content.append(lesson_content)
    
    def _combine_lesson_content(self, lesson):
        """Combine all lesson content into searchable text"""
        content_parts = []
        
        # Add metadata
        content_parts.append(f"Topic: {lesson.get('topic', '')}")
        content_parts.append(f"Title: {lesson.get('title', '')}")
        
        # Add learning objectives
        if "learning_objectives" in lesson:
            content_parts.append("Objectives: " + "; ".join(lesson["learning_objectives"]))
        
        # Add theory
        if "theory_explanation" in lesson:
            content_parts.append("Theory: " + " ".join(lesson["theory_explanation"]))
        
        # Add formulas
        if "key_formulas" in lesson:
            content_parts.append("Formulas: " + "; ".join(lesson["key_formulas"]))
        
        if "key_identities" in lesson:
            content_parts.append("Identities: " + "; ".join(lesson["key_identities"]))
        
        # Add examples
        if "worked_examples" in lesson:
            for example in lesson["worked_examples"]:
                content_parts.append(f"Example: {example.get('question', '')}")
        
        # Add exercises
        if "practice_exercises" in lesson:
            for exercise in lesson["practice_exercises"]:
                content_parts.append(f"Exercise: {exercise.get('question', '')}")
        
        return " ".join(content_parts)
    
    def create_lesson_embeddings(self):
        """Create semantic embeddings for all lesson content"""
        print("   🔄 Creating lesson embeddings...")
        
        if not self.lesson_content and not self.concept_explanations:
            print("   ⚠️  No lesson content to create embeddings")
            return
        
        # Create embeddings for different types of content
        all_content = []
        
        # Add lesson topics
        for topic in self.lesson_topics:
            all_content.append(topic)
        
        # Add concept explanations
        for concept in self.concept_explanations:
            all_content.append(concept['content'])
        
        # Add example questions
        for example in self.worked_examples:
            all_content.append(example['question'])
        
        # Add exercise questions
        for exercise in self.practice_exercises:
            all_content.append(exercise['question'])
        
        # Create embeddings
        if all_content:
            self.lesson_embeddings = self.semantic_model.encode(all_content)
            print(f"   ✅ Created embeddings for {len(all_content)} lesson items")
        else:
            print("   ⚠️  No content available for embeddings")
    
    def train(self):
        """Train the dedicated lesson model"""
        print("📚 TRAINING DEDICATED LESSON GENERATOR")
        
        # Load dataset
        self.dataset = self.load_dataset()
        
        if not self.dataset:
            print("   ❌ Cannot train lesson generator: No dataset loaded")
            return False
        
        # Extract lessons from dataset
        self.extract_lessons_from_dataset()
        
        if not self.lesson_metadata:
            print("   ⚠️  No lessons found for training")
            return False
        
        print(f"   📖 Loaded {len(self.lesson_topics)} lesson topics")
        print(f"   💡 Found {len(self.concept_explanations)} concept explanations")
        print(f"   📝 Found {len(self.worked_examples)} worked examples")
        print(f"   🏋️ Found {len(self.practice_exercises)} practice exercises")
        
        # Load semantic model
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create embeddings
        self.create_lesson_embeddings()
        
        # Save lesson model
        model_data = {
            'lesson_metadata': self.lesson_metadata,
            'lesson_topics': self.lesson_topics,
            'lesson_content': self.lesson_content,
            'concept_explanations': self.concept_explanations,
            'worked_examples': self.worked_examples,
            'practice_exercises': self.practice_exercises,
            'lesson_embeddings': self.lesson_embeddings,
            'semantic_model': self.semantic_model
        }
        
        joblib.dump(model_data, LESSON_MODEL_PATH)
        print(f"💾 Lesson Generator saved at {LESSON_MODEL_PATH}")
        print("🎉 Lesson Generator training complete!")
        print(f"📊 Lesson Statistics:")
        print(f"   - Topics: {len(self.lesson_topics)}")
        print(f"   - Concepts: {len(self.concept_explanations)}")
        print(f"   - Examples: {len(self.worked_examples)}")
        print(f"   - Exercises: {len(self.practice_exercises)}")
        
        return True

class TrueAITutor:
    def __init__(self):
        self.dataset = self.load_dataset()
        self.semantic_model = None
        self.vectorizer = None
        self.question_embeddings = None
        self.questions = []
        self.solutions = []
        self.alternative_solutions = []
        self.final_answers = []
        self.categories = []
        self.question_ids = []
        self.plotting_data = []
        
        # AI Learning Components
        self.similarity_threshold = 0.0
        self.question_patterns = {}
    
    def load_dataset(self):
        """Load the trigonometric dataset"""
        try:
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print("❌ trig_dataset.json not found")
            return {}
    
    def extract_training_data(self):
        """Extract questions, solutions, AND graph data - FIXED VERSION"""
        questions = []
        solutions = []
        alternative_solutions = []
        final_answers = []
        categories = []
        question_ids = []
        plotting_data = []
        
        print("   🔍 Extracting questions and graph data...")
        
        for category_name, items in self.dataset.items():
            if category_name != "metadata" and category_name != "lessons" and isinstance(items, list):
                print(f"      Processing category: {category_name} ({len(items)} items)")
                
                for item in items:
                    if isinstance(item, dict) and "question" in item:
                        questions.append(item["question"])
                        categories.append(category_name)
                        question_ids.append(item.get("id", "unknown"))
                        
                        # Extract final_answer if available
                        final_answer = item.get("final_answer", "")
                        final_answers.append(final_answer)
                        
                        # Main solution
                        if "step_by_step_solution" in item:
                            main_sol = item["step_by_step_solution"]
                        elif "solution" in item:
                            main_sol = [item["solution"]] if isinstance(item["solution"], str) else item["solution"]
                        else:
                            main_sol = ["Solution not available"]
                        solutions.append(main_sol)
                        
                        # Alternative solution
                        alt_sol = []
                        for field in ["alternative_solution", "alternative_method", "method_2"]:
                            if field in item:
                                if isinstance(item[field], str):
                                    alt_sol = [item[field]]
                                else:
                                    alt_sol = item[field]
                                break
                        alternative_solutions.append(alt_sol)
                        
                        # Extract plotting data
                        plot_info = {}
                        
                        if "plotting_instructions" in item and item["plotting_instructions"]:
                            plot_info = item["plotting_instructions"]
                            print(f"        📈 Found plotting_instructions for: {item.get('id', 'unknown')}")
                        
                        if "matplotlib_code" in item and item["matplotlib_code"]:
                            plot_info["matplotlib_code"] = item["matplotlib_code"]
                            print(f"        📊 Found matplotlib_code for: {item.get('id', 'unknown')}")
                        
                        question_lower = item["question"].lower()
                        if any(keyword in question_lower for keyword in ['sketch', 'graph', 'plot', 'draw']):
                            if not plot_info:
                                plot_info = {"needs_graph": True, "question_type": "graph"}
                        
                        plotting_data.append(plot_info)
        
        return questions, solutions, alternative_solutions, final_answers, categories, question_ids, plotting_data
    
    def _learn_semantic_relationships(self):
        """AI learns how questions relate to each other semantically"""
        print("   🔍 Learning semantic relationships...")
        
        sample_similarities = []
        for i in range(min(100, len(self.questions))):
            for j in range(i+1, min(i+20, len(self.questions))):
                sim = cosine_similarity(
                    [self.question_embeddings[i]], 
                    [self.question_embeddings[j]]
                )[0][0]
                sample_similarities.append(sim)
        
        if sample_similarities:
            self.similarity_threshold = np.percentile(sample_similarities, 80)
        else:
            self.similarity_threshold = 0.7
        
        print(f"   ✅ Learned optimal similarity threshold: {self.similarity_threshold:.3f}")
    
    def _ai_analyze_question_intent(self, question):
        """AI analyzes what the question is asking for, including graphs"""
        question_lower = question.lower()
        
        intent = {
            'type': 'unknown',
            'patterns': [],
            'operations': [],
            'functions': [],
            'needs_graph': False
        }
        
        if any(word in question_lower for word in ['prove', 'verify', 'show that', 'identity']):
            intent['type'] = 'proof'
            intent['patterns'].append('type_proof')
        elif any(word in question_lower for word in ['solve', 'find', 'value of']):
            intent['type'] = 'solve'
            intent['patterns'].append('type_solve')
        elif any(word in question_lower for word in ['sketch', 'graph', 'plot']):
            intent['type'] = 'graph'
            intent['patterns'].append('type_graph')
            intent['needs_graph'] = True
        
        math_funcs = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot']
        for func in math_funcs:
            if func in question_lower:
                intent['functions'].append(func)
                intent['patterns'].append(f'func_{func}')
        
        graph_keywords = ['sketch', 'graph', 'plot', 'draw', 'curve', 'wave']
        if any(keyword in question_lower for keyword in graph_keywords):
            intent['needs_graph'] = True
            intent['patterns'].append('needs_visualization')
        
        return intent
    
    def _learn_question_categories(self):
        """AI learns patterns in question types - FIXED VERSION"""
        print("   🔍 Learning question patterns...")
        
        pattern_counts = {}
        for i, question in enumerate(self.questions):
            intent = self._ai_analyze_question_intent(question)
            
            for pattern in intent['patterns']:
                if pattern not in self.question_patterns:
                    self.question_patterns[pattern] = []
                    pattern_counts[pattern] = 0
                self.question_patterns[pattern].append(i)
                pattern_counts[pattern] += 1
        
        print(f"   ✅ Learned {len(self.question_patterns)} question patterns")
        top_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for pattern, count in top_patterns:
            print(f"      {pattern}: {count} questions")
    
    def train_ai_understanding(self):
        """AI learns to understand questions including graph-related ones"""
        print("🧠 AI LEARNING: Understanding question patterns...")
        
        print("   📥 Loading semantic model...")
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("   🔄 Creating question embeddings...")
        self.question_embeddings = self.semantic_model.encode(self.questions)
        
        self._learn_semantic_relationships()
        self._learn_question_categories()
        
        print("✅ AI Understanding Training Complete!")
    
    def train(self):
        """Train the AI tutor with graph support"""
        print("🚀 TRUE AI TUTOR TRAINING")
        print("Learning to understand questions, using dataset answers + graphs")
        
        (self.questions, self.solutions, self.alternative_solutions, 
         self.final_answers, self.categories, self.question_ids, self.plotting_data) = self.extract_training_data()
        
        if not self.questions:
            print("❌ No questions found in dataset!")
            return
        
        print(f"📊 Training AI on {len(self.questions)} dataset questions")
        print(f"📝 Found {sum(1 for fa in self.final_answers if fa)} questions with final_answer field")
        
        graph_questions = sum(1 for p in self.plotting_data if p and (p.get('matplotlib_code') or p.get('function_type')))
        print(f"📈 Found {graph_questions} questions with graph data")
        
        self.train_ai_understanding()
        
        print("\n" + "="*60)
        print("📚 TRAINING LESSON GENERATOR")
        lesson_generator = LessonGenerator()
        lesson_trained = lesson_generator.train()
        
        model_data = {
            'questions': self.questions,
            'solutions': self.solutions,
            'alternative_solutions': self.alternative_solutions,
            'final_answers': self.final_answers,
            'categories': self.categories,
            'question_ids': self.question_ids,
            'plotting_data': self.plotting_data,
            'semantic_model': self.semantic_model,
            'question_embeddings': self.question_embeddings,
            'similarity_threshold': self.similarity_threshold,
            'question_patterns': self.question_patterns,
            'has_lesson_model': lesson_trained
        }
        
        joblib.dump(model_data, MODEL_PATH)
        print(f"💾 True AI Tutor saved at {MODEL_PATH}")
        print("🎉 AI can now understand questions AND generate graphs!")
        print(f"📊 Graph-ready questions: {graph_questions}")
        print(f"📝 Questions with final_answer: {sum(1 for fa in self.final_answers if fa)}")

def train_model():
    """Main training function"""
    tutor = TrueAITutor()
    tutor.train()

if __name__ == "__main__":
    train_model()