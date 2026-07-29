**SineWise - AI-Powered Trigonometry Tutor**
**Overview**
SineWise is a web-based tutoring system that provides personalized trigonometry instruction aligned with the Namibia NSSCAS Mathematics syllabus. It uses AI to deliver step-by-step solutions, generate practice questions, and help students prepare for examinations.
The system features an interactive chat interface where students can ask questions and receive detailed responses with complete worked solutions. It supports graph visualization, topic detection, and progress tracking.

**Features**
AI-Powered Tutoring
- Intelligent Question Answering: Ask any trigonometry question and get detailed, syllabus-aligned responses
- Step-by-Step Solutions: Complete worked solutions with all mathematical steps shown
- Graph Visualization: Automatic generation of trigonometric function graphs
- Concept Extraction: Automatic identification and explanation of key mathematical concepts

**Namibia Syllabus Alignment**
NSSCAS 8227 Compliance: All content follows the Namibia Ministry of Education syllabus
- Examination-Style Questions: Practice with questions formatted like actual exams
- Real-World Applications: Examples using Namibia-relevant contexts (agriculture, construction, environment)
- Local Standards: 3 significant figures, degrees to 1 decimal place, proper scientific notation


**Lesson Management**
- Structured Learning Paths: Organized topics following the Namibia syllabus sequence
- Progress Tracking: Monitor completion percentages and learning progress
- Active Lessons: Continue where you left off across sessions
- Multiple Topics: Comprehensive coverage of all trigonometry topics

**Technology Stack**
*Frontend*
- React 18 - Modern UI framework

- Bootstrap 5 - Responsive styling

- Axios - HTTP client for API calls


*Backend*
- Python Flask - API server

- Groq AI (Llama 3.1 8B) - AI model for intelligent responses

- NumPy/Matplotlib - Graph generation

- RESTful API - Clean interface between frontend and backend

Installation
**Prerequisites**
Node.js (v16 or higher)

Python (v3.8 or higher)

npm or yarn

Groq API Key (free from console.groq.com)

**1. Clone the Repository**
bash
git clone https://github.com/yourusername/sinewise.git
cd sinewise
**2. Frontend Setup**
bash
npm install
npm run dev
**3. Backend Setup**
bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python app.py
