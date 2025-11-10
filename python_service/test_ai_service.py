#!/usr/bin/env python3
"""
Unit tests for AI Service connection and functionality
Run with: python test_ai_service.py
"""

import os
import sys
import json
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from ai_service import AIService

class AIServiceTester:
    def __init__(self):
        self.ai_service = AIService()
        self.test_results = []
    
    def run_all_tests(self):
        """Run all connection and functionality tests"""
        print("🧪 AI Service Test Suite")
        print("=" * 50)
        
        # Test 1: Environment Variables
        self.test_environment_variables()
        
        # Test 2: API Connection
        self.test_api_connection()
        
        # Test 3: Lesson Content Generation
        self.test_lesson_generation()
        
        # Test 4: Q&A Functionality
        self.test_qa_functionality()
        
        # Print Summary
        self.print_test_summary()
    
    def test_environment_variables(self):
        """Test if environment variables are properly loaded"""
        print("\n🔧 Test 1: Environment Variables")
        print("-" * 30)
        
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key:
            print(f"✅ GROQ_API_KEY found: {api_key[:8]}...{api_key[-4:]}")
            self.test_results.append(("Environment Variables", "PASS", "API key loaded successfully"))
        else:
            print("❌ GROQ_API_KEY not found in environment")
            print("   Make sure .env file exists with: GROQ_API_KEY=your_key_here")
            self.test_results.append(("Environment Variables", "FAIL", "API key not found"))
    
    def test_api_connection(self):
        """Test basic API connection with a simple prompt"""
        print("\n📡 Test 2: API Connection")
        print("-" * 30)
        
        try:
            test_prompt = "Respond with only this exact JSON: {\"status\": \"connected\", \"message\": \"API test successful\"}"
            
            response = self.ai_service._call_ai_api(test_prompt)
            
            if "error" in response.lower():
                print(f"❌ API Connection Failed: {response}")
                self.test_results.append(("API Connection", "FAIL", f"Error: {response}"))
            else:
                print("✅ API Connection Successful")
                print(f"   Response: {response[:100]}...")
                self.test_results.append(("API Connection", "PASS", "Successfully connected to Groq API"))
                
        except Exception as e:
            print(f"❌ API Connection Exception: {e}")
            self.test_results.append(("API Connection", "FAIL", f"Exception: {e}"))
    
    def test_lesson_generation(self):
        """Test lesson content generation with a simple topic"""
        print("\n📚 Test 3: Lesson Content Generation")
        print("-" * 30)
        
        try:
            # Test with a simple mathematics topic
            lesson_content = self.ai_service.generate_lesson_content(
                topic_id="algebra",
                section_index=0,
                student_level="beginner"
            )
            
            if "error" in str(lesson_content).lower():
                print(f"❌ Lesson Generation Failed: {lesson_content}")
                self.test_results.append(("Lesson Generation", "FAIL", "Error in response"))
            else:
                print("✅ Lesson Generation Successful")
                print(f"   Title: {lesson_content.get('title', 'No title')}")
                print(f"   Content Points: {len(lesson_content.get('content', []))}")
                print(f"   Examples: {len(lesson_content.get('worked_examples', []))}")
                self.test_results.append(("Lesson Generation", "PASS", "Successfully generated lesson content"))
                
        except Exception as e:
            print(f"❌ Lesson Generation Exception: {e}")
            self.test_results.append(("Lesson Generation", "FAIL", f"Exception: {e}"))
    
    def test_qa_functionality(self):
        """Test Q&A functionality with a simple math question"""
        print("\n❓ Test 4: Q&A Functionality")
        print("-" * 30)
        
        try:
            test_question = "What is 2 + 2?"
            
            qa_response = self.ai_service.answer_student_question(
                question=test_question,
                topic_id="algebra"
            )
            
            if "error" in str(qa_response).lower():
                print(f"❌ Q&A Failed: {qa_response}")
                self.test_results.append(("Q&A Functionality", "FAIL", "Error in response"))
            else:
                print("✅ Q&A Functionality Successful")
                print(f"   Explanation: {qa_response.get('explanation', 'No explanation')[:50]}...")
                print(f"   Steps: {len(qa_response.get('steps', []))}")
                self.test_results.append(("Q&A Functionality", "PASS", "Successfully answered question"))
                
        except Exception as e:
            print(f"❌ Q&A Exception: {e}")
            self.test_results.append(("Q&A Functionality", "FAIL", f"Exception: {e}"))
    
    
    
    def print_test_summary(self):
        """Print a summary of all test results"""
        print("\n" + "=" * 50)
        print(" TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASS")
        total = len(self.test_results)
        
        print(f"Overall Result: {passed}/{total} Tests Passed")
        
        for test_name, status, message in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {status} - {message}")
        
        print("\n" + "=" * 50)
        if passed == total:
            print(" ALL TESTS PASSED! AI Service is working correctly.")
        else:
            print(" Some tests failed. Check the configuration and try again.")
        
        return passed == total

def quick_connection_test():
    """Run a quick connection test only"""
    print("🔍 Quick Connection Test")
    print("-" * 30)
    
    tester = AIServiceTester()
    
    # Test only environment and connection
    tester.test_environment_variables()
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        tester.test_api_connection()
    
    # Print mini summary
    print("\n📋 Quick Test Results:")
    for test_name, status, message in tester.test_results:
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"   {status_icon} {test_name}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AI Service Connection")
    parser.add_argument("--quick", action="store_true", help="Run quick connection test only")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_connection_test()
    else:
        tester = AIServiceTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)