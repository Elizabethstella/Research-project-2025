# ai_service.py
import os
import json
from typing import Dict, List, Any
import requests
from pathlib import Path 
from dotenv import load_dotenv 

project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

print(f"🔍 Looking for .env at: {env_path}")

if env_path.exists():
    load_dotenv(env_path)
    print("✅ .env loaded from project root!")
else:
    print("❌ .env not found at project root")
    # Fallback to current directory
    load_dotenv()
    print(f"📁 Trying current directory: {os.getcwd()}")
from namibia_syllabus_context import get_syllabus_context, get_topic_specific_prompt, generate_namibia_style_question

class AIService:
    def __init__(self):
        # Choose your preferred API - DeepSeek is free, OpenAI requires payment
        
        self.api_key = os.getenv("GROQ_API_KEY") 
        
        if not self.api_key:
            print("❌ CRITICAL: No GROQ_API_KEY found!")
            print("   Get free API key from: https://console.groq.com")
        else:
            print(f"✅ Groq API Key loaded: {self.api_key[:8]}...")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"  
        
        print(f"🤖 AI Service: Groq + {self.model}")
    
    def generate_lesson_content(self, topic_id: str, section_index: int, student_level: str = "beginner") -> Dict[str, Any]:
        """Generate Namibia syllabus-aligned lesson content"""
        
        syllabus_context = get_syllabus_context(topic_id)
        topic_focus = get_topic_specific_prompt(topic_id, section_index)
        
        prompt = f"""
        {syllabus_context}
        
        You are an expert mathematics teacher in Namibia preparing students for the NSSCAS Advanced Subsidiary Level examination (Syllabus Code: 8227).
        
        TASK: Generate a comprehensive lesson section that strictly follows the Namibia syllabus requirements.
        
        TOPIC FOCUS: {topic_focus}
        SECTION: {section_index + 1}
        STUDENT LEVEL: {student_level}
        
        REQUIREMENTS:
        - Content must align exactly with Namibia syllabus specific objectives
        - Include Namibia-relevant examples (agriculture, construction, environment)
        - Use examination-style practice questions
        - Provide step-by-step solutions showing all working
        - Follow accuracy standards: 3 significant figures, degrees to 1 decimal place
        - Prepare students for structured examination questions
        
        
        Please provide the lesson content in this exact JSON format:
        {{
            "title": "section title aligned with syllabus",
            "content": [
                "key learning point 1 with syllabus alignment",
                "key learning point 2 with practical application",
                "key learning point 3 with examination focus"
            ],
            "worked_examples": [
                {{
                    "problem": "Namibia examination-style problem",
                    "solution": "step-by-step solution showing all working",
                    "explanation": "syllabus concepts and examination techniques"
                }}
            ],
            "applications": [
                "Namibia-relevant application 1",
                "Namibia-relevant application 2"
            ],
            "practice_questions": [
                {{
                    "question": "examination-style question",
                    "hint": "guidance for solving",
                    "answer": "detailed solution"
                }}
            ],
            "syllabus_alignment": {{
                "covered_objectives": ["specific objective 1", "specific objective 2"],
                "assessment_preparation": "how this prepares for examination"
            }}
        }}
        """
        
        response = self._call_ai_api(prompt)
        return self._parse_lesson_response(response)
    
    def answer_student_question(self, question: str, topic_id: str, conversation_history: List = None) -> Dict[str, Any]:
        
       """Answer student questions with Namibia syllabus alignment"""
    
       syllabus_context = get_syllabus_context(topic_id)
    
       prompt = f"""
       {syllabus_context}

       STUDENT QUESTION: "{question}"

       REQUIREMENTS:
       - Provide COMPLETE step-by-step solutions
       - Show ALL mathematical working
       - Number ALL steps (Step 1, Step 2, Step 3...)
       - Do NOT skip any steps
       - Ensure final answer is clearly stated
       - Use proper fractions (1/2 NOT 1/)

       Format response as JSON:
       {{
        "explanation": "clear explanation",
        "steps": [
            "Step 1: [complete first step]",
            "Step 2: [complete second step]", 
            "Step 3: [complete third step]"
        ],
        "worked_example": {{
            "problem": "practice problem",
            "solution": [
                "Step 1: [complete step]",
                "Step 2: [complete step]"
            ]
        }},
        "key_concepts": ["concept 1", "concept 2"],
        "examination_tips": ["tip 1", "tip 2"]
    }}

        IMPORTANT: Make sure ALL steps are complete and nothing is cut off.
        """
    
       response = self._call_ai_api(prompt)
       return self._parse_qa_response(response)
    
    def generate_assessment_questions(self, topic_id: str, question_type: str, difficulty: str, num_questions: int = 5) -> List[Dict]:
        """Generate Namibia examination-style assessment questions"""
        
        syllabus_context = get_syllabus_context(topic_id)
        
        prompt = f"""
        {syllabus_context}
        
        TASK: Generate {num_questions} {difficulty} difficulty {question_type} questions in Namibia NSSCAS examination style.
        
        EXAMINATION REQUIREMENTS:
        - Structured questions with clear parts (a), (b), (c) where appropriate
        - Real-world contexts relevant to Namibia
        - Step-by-step reasoning required
        - Accuracy: 3 significant figures, degrees to 1 decimal place
        - Non-programmable scientific calculator permitted
        
        Format as JSON array:
        [
            {{
                "question_id": "q1",
                "question": "Namibia examination-style question text",
                "parts": ["(a) sub-question", "(b) sub-question"] (if applicable),
                "options": ["A", "B", "C", "D"] (for multiple choice),
                "correct_answer": "detailed solution showing all working",
                "explanation": "syllabus concepts and examination techniques",
                "concepts": ["syllabus concept 1", "syllabus concept 2"],
                "difficulty": "{difficulty}",
                "marks": 4
            }}
        ]
        """
        
        response = self._call_ai_api(prompt)
        return self._parse_assessment_response(response)
    
    def clean_ai_response(self, response: str) -> str:
        """Clean AI response to extract pure JSON"""
    # Remove all text before first [ and after last ]
        start = response.find('[')
        end = response.rfind(']') + 1
    
        if start != -1 and end != -1:
          return response[start:end]
    
    # Fallback: try to extract from markdown
        if '```json' in response:
           start = response.find('```json') + 7
           end = response.find('```', start)
           if end != -1:
              return response[start:end]
    
        return response  # Return as-is if no cleaning worked
    
    def _call_ai_api(self, prompt: str) -> str:
        """Call the AI API"""
        try:
            if not self.api_key:
                return json.dumps({"error": "No API key configured"})
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert Namibia NSSCAS Mathematics examiner and teacher. Always provide accurate, syllabus-aligned responses with step-by-step working. Always return valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            print(f"🤖 Calling AI API with model: {self.model}")
            response = requests.post(f"{self.base_url}/chat/completions", 
                                   headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()["choices"][0]["message"]["content"]
            print("✅ AI API call successful")
            return result
            
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return self._get_fallback_response()
    
    def _parse_lesson_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for lesson content"""
        try:
            # Clean the response (sometimes AI adds extra text)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse lesson response: {e}")
            print(f"Raw response: {response}")
            return self._get_default_lesson()
    
    def _parse_qa_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for Q&A"""
        try:
           response = response.strip()
        
        # Remove markdown code blocks if present
           if response.startswith("```json"):
              response = response[7:]
           if response.endswith("```"):
             response = response[:-3]
           response = response.strip()
        
        # Extract only the JSON part
           start_idx = response.find('{')
           end_idx = response.rfind('}') + 1
        
           if start_idx == -1 or end_idx == 0:
              raise json.JSONDecodeError("No JSON object found", response, 0)
         
           json_str = response[start_idx:end_idx]
           parsed_data = json.loads(json_str)
        
        # Extract and clean answer text
           answer_text = response[end_idx:].strip()
           if answer_text:
            # Remove server log lines
              lines = answer_text.split('\n')
              clean_lines = []
              for line in lines:
                  line = line.strip()
                # Skip common log patterns
                  if (line.startswith('127.0.0.1') or 
                     line.startswith('HTTP') or 
                     line.startswith('POST') or 
                     line.startswith('GET')):
                     continue
                  if line:
                     clean_lines.append(line)
            
              clean_answer = '\n'.join(clean_lines)
              if clean_answer:
                 parsed_data["extracted_answer"] = clean_answer
        
           return parsed_data
        except json.JSONDecodeError as e:
         print(f"❌ Failed to parse Q&A response: {e}")
         print(f"Raw response: {response}")
         return self._get_default_qa_response()
    
    def _parse_assessment_response(self, response: str) -> List[Dict]:
        """Parse AI response for assessments"""
        try:
            response = self.clean_ai_response(response.strip())
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse assessment response: {e}")
            print(f"Raw response: {response}")
        return self._get_default_assessment()
    
    def _get_fallback_response(self):
        return json.dumps({"error": "AI service unavailable"})
    
    def _get_default_lesson(self):
        return {
            "title": "Namibia NSSCAS Mathematics",
            "content": ["Please check your API configuration for Namibia syllabus content."],
            "worked_examples": [],
            "applications": [],
            "practice_questions": [],
            "syllabus_alignment": {
                "covered_objectives": [],
                "assessment_preparation": "Basic content delivery"
            }
        }
    
    def _get_default_qa_response(self):
        return {
            "explanation": "I'm currently unable to answer questions. Please check your API configuration.",
            "steps": [],
            "worked_example": {},
            "key_concepts": [],
            "examination_tips": []
        }
    
    def _get_default_assessment(self):
        return []