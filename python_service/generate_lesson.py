# python_service/generate_lesson.py

import joblib
import os
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Define paths to model and dataset
BASE_DIR = os.path.dirname(__file__)
LESSON_MODEL_PATH = os.path.join(BASE_DIR, "lesson_generator.pkl")  # Match your lesson generator
DATASET_PATH = os.path.join(BASE_DIR, "trig_dataset.json")

# Load the trained lesson model once (for performance)
if os.path.exists(LESSON_MODEL_PATH):
    lesson_model = joblib.load(LESSON_MODEL_PATH)
    print("✅ Lesson Generator model loaded successfully!")
else:
    lesson_model = None
    print("⚠️ No trained lesson model found. Please train the model first using model_trainer.py")

if os.path.exists(DATASET_PATH):
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)
else:
    dataset = {}
    print("⚠️ No dataset found. Please add trig_dataset.json")

def generate_lesson_from_topic(topic: str) -> dict:
    """
    Generates or retrieves a lesson using the lesson generator model.
    Matches the structure of your LessonGenerator class.
    """
    topic = topic.strip().lower()

    if not topic:
        return {"error": "Topic is required"}

    if not lesson_model:
        return {"error": "Lesson generator model not available"}

    try:
        # Use the lesson generator model to find relevant content
        user_embedding = lesson_model['semantic_model'].encode([topic])
        
        best_match = None
        highest_similarity = 0
        
        # Search through concept explanations
        for i, concept in enumerate(lesson_model['concept_explanations']):
            if i < len(lesson_model['lesson_embeddings']):
                concept_embedding = lesson_model['lesson_embeddings'][i]
                similarity = cosine_similarity(user_embedding, [concept_embedding])[0][0]
                
                if similarity > highest_similarity and similarity > 0.3:
                    highest_similarity = similarity
                    best_match = {
                        'type': 'concept',
                        'data': concept,
                        'similarity': similarity
                    }
        
        # Search through worked examples
        example_offset = len(lesson_model['concept_explanations'])
        for i, example in enumerate(lesson_model['worked_examples']):
            idx = example_offset + i
            if idx < len(lesson_model['lesson_embeddings']):
                example_embedding = lesson_model['lesson_embeddings'][idx]
                similarity = cosine_similarity(user_embedding, [example_embedding])[0][0]
                
                if similarity > highest_similarity and similarity > 0.3:
                    highest_similarity = similarity
                    best_match = {
                        'type': 'example',
                        'data': example,
                        'similarity': similarity
                    }
        
        # Search through practice exercises
        exercise_offset = example_offset + len(lesson_model['worked_examples'])
        for i, exercise in enumerate(lesson_model['practice_exercises']):
            idx = exercise_offset + i
            if idx < len(lesson_model['lesson_embeddings']):
                exercise_embedding = lesson_model['lesson_embeddings'][idx]
                similarity = cosine_similarity(user_embedding, [exercise_embedding])[0][0]
                
                if similarity > highest_similarity and similarity > 0.3:
                    highest_similarity = similarity
                    best_match = {
                        'type': 'exercise',
                        'data': exercise,
                        'similarity': similarity
                    }
        
        if best_match:
            return _format_lesson_response(best_match, topic, highest_similarity)
        else:
            return {"error": f"No relevant lesson content found for topic: {topic}"}
            
    except Exception as e:
        return {"error": f"Lesson generation failed: {str(e)}"}

def _format_lesson_response(match, original_topic, confidence):
    """Format the lesson response based on match type"""
    
    if match['type'] == 'concept':
        concept = match['data']
        return {
            "topic": original_topic.title(),
            "matched_topic": concept['topic'],
            "lesson_type": "concept_explanation",
            "content": concept['content'],
            "lesson_id": concept.get('lesson_id', ''),
            "confidence": float(confidence),
            "source": "Lesson Generator - Concept"
        }
    
    elif match['type'] == 'example':
        example = match['data']
        return {
            "topic": original_topic.title(),
            "matched_topic": example['topic'],
            "lesson_type": "worked_example",
            "title": example.get('title', ''),
            "question": example['question'],
            "solution": example.get('solution', []),
            "explanation": example.get('explanation', ''),
            "difficulty": example.get('difficulty', 'Unknown'),
            "confidence": float(confidence),
            "source": "Lesson Generator - Example"
        }
    
    elif match['type'] == 'exercise':
        exercise = match['data']
        return {
            "topic": original_topic.title(),
            "matched_topic": exercise['topic'],
            "lesson_type": "practice_exercise",
            "question": exercise['question'],
            "solution": exercise.get('solution', []),
            "final_answer": exercise.get('final_answer', ''),
            "difficulty": exercise.get('difficulty', 'Unknown'),
            "confidence": float(confidence),
            "source": "Lesson Generator - Exercise"
        }

def get_available_topics():
    """Get list of available lesson topics from the model"""
    if not lesson_model:
        return []
    
    topics = set()
    for concept in lesson_model.get('concept_explanations', []):
        topics.add(concept.get('topic', ''))
    
    for example in lesson_model.get('worked_examples', []):
        topics.add(example.get('topic', ''))
    
    for exercise in lesson_model.get('practice_exercises', []):
        topics.add(exercise.get('topic', ''))
    
    return list(topics)

def get_lesson_statistics():
    """Get statistics about available lessons"""
    if not lesson_model:
        return {"error": "Lesson model not available"}
    
    return {
        "total_concepts": len(lesson_model.get('concept_explanations', [])),
        "total_examples": len(lesson_model.get('worked_examples', [])),
        "total_exercises": len(lesson_model.get('practice_exercises', [])),
        "available_topics": len(get_available_topics()),
        "model_loaded": True
    }

# Example usage and testing
if __name__ == "__main__":
    # Test the lesson generator
    test_topics = [
        "unit circle",
        "sine function", 
        "trigonometric identities",
        "graphing cosine",
        "exact values"
    ]
    
    print("🧠 LESSON GENERATOR TEST")
    print("=" * 50)
    
    stats = get_lesson_statistics()
    if "error" not in stats:
        print(f"📊 Model Statistics:")
        print(f"   Concepts: {stats['total_concepts']}")
        print(f"   Examples: {stats['total_examples']}")
        print(f"   Exercises: {stats['total_exercises']}")
        print(f"   Topics: {stats['available_topics']}")
    
    print(f"\n🎯 Available Topics (sample):")
    topics = get_available_topics()
    for topic in topics[:5]:
        print(f"   • {topic}")
    if len(topics) > 5:
        print(f"   ... and {len(topics) - 5} more")
    
    print(f"\n🔍 Testing Lesson Generation:")
    for topic in test_topics:
        result = generate_lesson_from_topic(topic)
        print(f"\n📚 Topic: '{topic}'")
        if "error" in result:
            print(f"   ❌ {result['error']}")
        else:
            print(f"   ✅ Matched: {result.get('matched_topic', 'N/A')}")
            print(f"   📖 Type: {result.get('lesson_type', 'N/A')}")
            print(f"   🎯 Confidence: {result.get('confidence', 0):.3f}")
            print(f"   📝 Source: {result.get('source', 'N/A')}")
            
            # Show preview of content
            if 'content' in result:
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                print(f"   💡 Content: {content_preview}")
            elif 'question' in result:
                print(f"   ❓ Question: {result['question']}")