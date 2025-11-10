# ai_lesson_generator.py
import json
import joblib
import os
from typing import Dict, List, Any
from ai_service import AIService

class AILessonGenerator:
    def __init__(self):
        self.ai_service = AIService()
        self.is_trained = True
        
    def train_lesson_generator(self):
        """No training needed for API-based service"""
        print("🎓 AI Lesson Generator ready (API-based)")
        return True

    def generate_ai_lesson(self, topic_id: str, section_index: int) -> Dict[str, Any]:
        """Generate AI-powered lesson content using Namibia syllabus"""
        print(f"🤖 Generating Namibia syllabus lesson for {topic_id}, section {section_index}")
        
        try:
            # Get AI-generated content with Namibia context
            ai_content = self.ai_service.generate_lesson_content(topic_id, section_index)
            
            # Build comprehensive lesson structure
            lesson_structure = {
                'topic_id': topic_id,
                'title': f"Namibia NSSCAS: {ai_content.get('title', topic_id.replace('_', ' ').title())}",
                'description': f"Namibia Syllabus 8227 - {topic_id.replace('_', ' ').title()}",
                'current_section': {
                    'title': ai_content.get('title', f'Section {section_index + 1}'),
                    'content': ai_content.get('content', []),
                    'worked_examples': ai_content.get('worked_examples', []),
                    'applications': ai_content.get('applications', []),
                    'misconceptions': ai_content.get('misconceptions', []),
                    'practice_questions': ai_content.get('practice_questions', []),
                    'ai_generated': True
                },
                'section_index': section_index,
                'total_sections': 4,
                'learning_objectives': self._generate_learning_objectives(topic_id),
                'ai_generated': True,
                'method': 'namibia_syllabus_ai',
                'syllabus_alignment': ai_content.get('syllabus_alignment', {})
            }
            
            print(f"✅ Generated Namibia lesson with {len(ai_content.get('content', []))} content points")
            return lesson_structure
            
        except Exception as e:
            print(f"❌ Error generating Namibia lesson: {e}")
            return self._get_fallback_lesson(topic_id, section_index)

    def answer_student_question(self, question: str, topic_id: str, conversation_history: List = None) -> Dict[str, Any]:
        """Answer student questions using Namibia syllabus AI"""
        try:
            response = self.ai_service.answer_student_question(question, topic_id, conversation_history)
            return {
                'success': True,
                'response': self._format_ai_response(response),
                'worked_example': response.get('worked_example', {}),
                'key_concepts': response.get('key_concepts', []),
                'examination_tips': response.get('examination_tips', []),
                'method': 'namibia_syllabus_qa'
            }
        except Exception as e:
            print(f"❌ Error answering question: {e}")
            return {
                'success': False,
                'response': "I'm having trouble answering right now. Please try again.",
                'method': 'namibia_syllabus_qa'
            }

    def _generate_learning_objectives(self, topic_id: str) -> List[str]:
        """Generate learning objectives based on Namibia syllabus"""
        objectives_map = {
            "circular_measure": [
                "Understand radian measure and convert between radians and degrees",
                "Solve problems involving arc length and sector area",
                "Apply circular measure to Namibian practical contexts",
                "Master Namibia examination techniques for circular measure"
            ],
            "trigonometric_graphs": [
                "Sketch and interpret trigonometric graphs using degrees and radians",
                "Determine amplitude, period and transformations of graphs",
                "Use exact values of trigonometric functions for standard angles",
                "Apply graph knowledge to Namibia examination questions"
            ],
            "trigonometric_identities": [
                "Prove and apply fundamental trigonometric identities",
                "Simplify trigonometric expressions using identities",
                "Use identities to solve Namibia-style problems",
                "Master identity proofs for NSSCAS examination"
            ],
            "trigonometric_equations": [
                "Solve trigonometric equations within specified intervals",
                "Find general solutions to trigonometric equations",
                "Apply identities in solving complex equations",
                "Prepare for Namibia examination equation solving"
            ],
            "advanced_trigonometry": [
                "Work with all six trigonometric functions and their graphs",
                "Apply compound and double angle formulae",
                "Express combinations in R-form for equation solving",
                "Master advanced trigonometry for Namibia syllabus"
            ]
        }
        return objectives_map.get(topic_id, [
            "Understand key mathematical concepts",
            "Apply knowledge to solve Namibia-style problems",
            "Develop examination techniques and strategies"
        ])

    def _format_ai_response(self, response: Dict) -> str:
        """Format AI response into readable text with Namibia focus"""
        formatted = "🎓 **Namibia NSSCAS Tutor Explanation:**\n\n"
        
        if response.get('explanation'):
            formatted += f"{response['explanation']}\n\n"
        
        if response.get('steps'):
            formatted += "**Step-by-Step Examination-style Solution:**\n"
            for i, step in enumerate(response['steps'], 1):
                formatted += f"{i}. {step}\n"
            formatted += "\n"
        
        if response.get('worked_example', {}).get('problem'):
            example = response['worked_example']
            formatted += f"**Examination Practice:**\n"
            formatted += f"Problem: {example['problem']}\n"
            if example.get('solution'):
                formatted += f"Solution: {example['solution']}\n\n"
        
        if response.get('key_concepts'):
            formatted += f"**Syllabus Concepts:** {', '.join(response['key_concepts'])}\n\n"
        
        if response.get('examination_tips'):
            formatted += "**Examination Tips:**\n"
            for tip in response['examination_tips']:
                formatted += f"• {tip}\n"
        
        formatted += "\n*Aligned with Namibia NSSCAS Mathematics Syllabus 8227*"
        return formatted

    def _get_fallback_lesson(self, topic_id: str, section_index: int) -> Dict[str, Any]:
        """Provide fallback Namibia syllabus lesson content"""
        return {
            'topic_id': topic_id,
            'title': f"Namibia NSSCAS: {topic_id.replace('_', ' ').title()}",
            'description': "Namibia Syllabus 8227 - Learning mathematical concepts",
            'current_section': {
                'title': f'Section {section_index + 1}: Introduction',
                'content': [
                    f"Exploring {topic_id.replace('_', ' ')} according to Namibia syllabus",
                    "Understanding key mathematical principles for NSSCAS examination",
                    "Building foundational knowledge with Namibia context"
                ],
                'worked_examples': [],
                'applications': ["Namibian practical applications"],
                'misconceptions': [],
                'practice_questions': []
            },
            'section_index': section_index,
            'total_sections': 4,
            'learning_objectives': self._generate_learning_objectives(topic_id),
            'ai_generated': False,
            'method': 'fallback',
            'syllabus_alignment': {
                'covered_objectives': ['Basic concept understanding'],
                'assessment_preparation': 'Foundation building'
            }
        }