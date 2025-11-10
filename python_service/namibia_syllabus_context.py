# namibia_syllabus_context.py - Updated with all trigonometry topics
"""
Namibia AS Mathematics Syllabus Context Integration
Based on NSSCAS Mathematics Syllabus Code: 8227
Official Syllabus for Implementation in 2021
"""

NAMIBIA_AS_MATHEMATICS_SYLLABUS = {
    "syllabus_code": "8227",
    "level": "NSSCAS Advanced Subsidiary Level",
    "examination_board": "Namibia Ministry of Education, Arts and Culture",
    "implementation_year": 2021,
    
    "trigonometry_topics": {
        "circular_measure": {
            "general_objective": "understand the relationship between radians and degrees and solve problems involving arc length and sector area",
            "specific_objectives": [
                "interpret the term radian and use the relationship between radians and degrees",
                "use the formulae s = rθ and A = ½r²θ to solve problems concerning the arc length, sector area of a circle and segment area"
            ],
            "assessment_requirements": [
                "Solve problems involving arc length and sector area",
                "Apply circular measure to practical contexts",
                "Convert between radians and degrees accurately"
            ]
        },
        "trigonometric_graphs": {
            "general_objective": "understand and use trigonometric graphs and their transformations",
            "specific_objectives": [
                "sketch and use graphs of the sine, cosine and tangent functions (for angles of any size, and using either degrees or radians)",
                "find the amplitude and period and sketch and interpret graphs of the form y = a sin(bx) + c, y = a cos(bx) + c, and y = a tan(bx) + c",
                "use the exact values of the sine, cosine and tangent of 30°, 45°, 60°, and related angles, e.g. cos 150° = -½√3",
                "use the notations sin⁻¹x, cos⁻¹x, tan⁻¹x to denote the principal values of the inverse trigonometric relations"
            ],
            "assessment_requirements": [
                "Sketch trigonometric graphs with correct amplitude and period",
                "Identify transformations from equations",
                "Use exact values for standard angles"
            ]
        },
        "trigonometric_identities": {
            "general_objective": "use trigonometric identities to prove identities and simplify expressions",
            "specific_objectives": [
                "use the trigonometric identities sinθ/cosθ = tanθ and sin²θ + cos²θ = 1 to prove identities",
                "apply identities to simplify trigonometric expressions",
                "use identities to determine unknown values in trigonometric expressions"
            ],
            "assessment_requirements": [
                "Prove trigonometric identities step by step",
                "Simplify complex trigonometric expressions",
                "Apply identities in problem-solving contexts"
            ]
        },
        "trigonometric_equations": {
            "general_objective": "solve trigonometric equations within specified intervals",
            "specific_objectives": [
                "find solutions, in degrees or radians and within a specified interval, of the equations sin(nx) = k, cos(nx) = k, tan(nx) = k",
                "solve equations easily reducible to these forms, where n is a small integer or a simple fraction",
                "apply trigonometric identities in solving equations"
            ],
            "assessment_requirements": [
                "Solve equations within specified intervals",
                "Show all working and reasoning",
                "Find all possible solutions in given ranges"
            ]
        },
        "advanced_trigonometry": {
            "general_objective": "understand and use advanced trigonometric functions and identities",
            "specific_objectives": [
                "recognise the relationship of the secant, cosecant and cotangent functions to cosine, sine and tangent",
                "use properties and graphs of all six trigonometric functions for angles of any magnitude",
                "use trigonometrical identities for the simplification and exact evaluation of expressions including:",
                "  - sec²θ = 1 + tan²θ and cosec²θ = 1 + cot²θ",
                "  - the expansions of sin(A ± B), cos(A ± B) and tan(A ± B)",
                "  - the formulae for sin 2A, cos 2A and tan 2A",
                "  - the expressions a sinθ ± b cosθ in the forms R sin(θ ± α) and R cos(θ ± α)"
            ],
            "assessment_requirements": [
                "Work with all six trigonometric functions",
                "Apply compound angle formulae",
                "Express combinations in R-form",
                "Solve complex trigonometric equations"
            ]
        }
    },
    
    "assessment_structure": {
        "paper_1_weighting": "50%",
        "paper_2_weighting": "50%", 
        "time_allocation": "2 hours per paper",
        "marks": "75 marks per paper",
        "question_style": "Structured questions with no choice of questions"
    },
    
    "grade_descriptors": {
        "grade_a": "Apply trigonometric identities to prove identities and solve trigonometric equations in more complex cases. Find solutions of trigonometric equations including equations easily reducible to standard forms. Use compound angle formulae and R-form expressions.",
        "grade_c": "Prove identities and solve trigonometric equations in simple cases. Use exact values of trigonometric functions for standard angles. Sketch and interpret trigonometric graphs.",
        "grade_e": "Use the notations sin⁻¹x, cos⁻¹x, tan⁻¹x to denote principal values. Sketch graphs of basic trigonometric functions. Solve simple trigonometric equations."
    },
    
    "mathematical_formulae": {
        "circular_measure": [
            "Arc length = rθ (θ in radians)",
            "Area of sector = ½r²θ (θ in radians)"
        ],
        "basic_identities": [
            "tan θ ≡ sin θ / cos θ",
            "cos²θ + sin²θ ≡ 1",
            "1 + tan²θ ≡ sec²θ",
            "cot²θ + 1 ≡ cosec²θ"
        ],
        "compound_angles": [
            "sin(A ± B) ≡ sin A cos B ± cos A sin B",
            "cos(A ± B) ≡ cos A cos B ∓ sin A sin B", 
            "tan(A ± B) ≡ (tan A ± tan B) / (1 ∓ tan A tan B)"
        ],
        "double_angles": [
            "sin 2A ≡ 2 sin A cos A",
            "cos 2A ≡ cos²A - sin²A ≡ 2 cos²A - 1 ≡ 1 - 2 sin²A",
            "tan 2A = 2 tan A / (1 - tan²A)"
        ],
        "exact_values": {
            "30° (π/6)": {"sin": "1/2", "cos": "√3/2", "tan": "1/√3"},
            "45° (π/4)": {"sin": "1/√2", "cos": "1/√2", "tan": "1"},
            "60° (π/3)": {"sin": "√3/2", "cos": "1/2", "tan": "√3"}
        }
    }
}

def get_syllabus_context(topic_id):
    """Get Namibia-specific syllabus context for curriculum alignment"""
    
    topic_info = NAMIBIA_AS_MATHEMATICS_SYLLABUS["trigonometry_topics"].get(topic_id, {})
    
    syllabus_context = f"""
    NAMIBIA NSSCAS MATHEMATICS SYLLABUS CONTEXT
    Syllabus Code: 8227 - Advanced Subsidiary Level
    Examination Board: Namibia Ministry of Education, Arts and Culture
    
    CURRICULUM ALIGNMENT REQUIREMENTS:
    - Content must align with NSSCAS Mathematics syllabus specific objectives
    - Assessment style: Structured questions with step-by-step reasoning
    - Accuracy standards: 3 significant figures, degrees to 1 decimal place
    - Calculator: Non-programmable scientific calculator permitted
    
    """
    
    if topic_info:
        syllabus_context += f"""
    TOPIC: {topic_id.replace('_', ' ').title()}
    GENERAL OBJECTIVE: {topic_info.get('general_objective', '')}
    
    SPECIFIC LEARNING OBJECTIVES:
    {chr(10).join(['• ' + obj for obj in topic_info.get('specific_objectives', [])])}
    
    ASSESSMENT REQUIREMENTS:
    {chr(10).join(['• ' + req for req in topic_info.get('assessment_requirements', [])])}
    
    GRADE EXPECTATIONS:
    A Grade: {NAMIBIA_AS_MATHEMATICS_SYLLABUS['grade_descriptors']['grade_a']}
    C Grade: {NAMIBIA_AS_MATHEMATICS_SYLLABUS['grade_descriptors']['grade_c']}
    E Grade: {NAMIBIA_AS_MATHEMATICS_SYLLABUS['grade_descriptors']['grade_e']}
    """
    
    return syllabus_context

def get_topic_specific_prompt(topic_id, section_index):
    """Get topic-specific prompts based on Namibia syllabus"""
    
    topic_prompts = {
        "circular_measure": [
            "Focus on radian definition and conversion between radians and degrees",
            "Apply arc length and sector area formulae to practical problems",
            "Solve problems involving segment area and combined figures", 
            "Contextual applications in Namibian agriculture and construction"
        ],
        "trigonometric_graphs": [
            "Graph sketching of sine, cosine, tangent functions using both degrees and radians",
            "Determining amplitude, period and transformations of trigonometric graphs",
            "Using exact values for 30°, 45°, 60° and related angles",
            "Inverse trigonometric functions and their graphs"
        ],
        "trigonometric_identities": [
            "Proving basic trigonometric identities step by step",
            "Using identities to simplify trigonometric expressions", 
            "Applying Pythagorean identities and ratio identities",
            "Identity proofs with logical reasoning and steps"
        ],
        "trigonometric_equations": [
            "Solving basic trigonometric equations within specified intervals",
            "Finding general solutions and specific solutions in given ranges",
            "Equations reducible to quadratic form in trigonometry",
            "Application problems involving trigonometric equations"
        ],
        "advanced_trigonometry": [
            "Secant, cosecant, cotangent functions and their graphs",
            "Compound angle formulae and their applications",
            "Double angle formulae and identity proofs",
            "R-form expressions: a sinθ ± b cosθ and their applications"
        ]
    }
    
    prompts = topic_prompts.get(topic_id, ["Apply mathematical concepts to solve problems"])
    current_prompt = prompts[section_index % len(prompts)]
    
    return f"Focus Area: {current_prompt}"

def generate_namibia_style_question(topic_id, difficulty="medium"):
    """Generate Namibia examination-style question prompts"""
    
    question_templates = {
        "circular_measure": [
            "A circular agricultural field in Namibia has a radius of 50m. Calculate the arc length subtended by an angle of 1.2 radians, and find the area of the corresponding sector.",
            "A water reservoir has a circular cross-section with radius 15m. If the water surface subtends an angle of 2.5 radians at the center, calculate the area of the water surface.",
            "Convert 150° to radians and 3π/4 radians to degrees. Show all working."
        ],
        "trigonometric_graphs": [
            "Sketch the graph of y = 2sin(3x) for 0° ≤ x ≤ 360°, indicating the amplitude and period.",
            "Find the exact value of: (a) sin 150° (b) cos 225° (c) tan 300°",
            "Solve the equation 2cos(2x) = 1 for 0° ≤ x ≤ 360°, showing all steps."
        ],
        "trigonometric_identities": [
            "Prove the identity: (1 - cos²θ)(1 + tan²θ) = tan²θ",
            "Simplify the expression: (sinθ + cosθ)² + (sinθ - cosθ)²",
            "Prove that secθ - cosθ = sinθ tanθ"
        ],
        "trigonometric_equations": [
            "Solve the equation 2sin²x - sinx - 1 = 0 for 0° ≤ x ≤ 360°",
            "Find all solutions to cos2x = 0.5 in the interval 0 ≤ x ≤ 2π",
            "Solve 3tan²x - 1 = 0 for 0° ≤ x ≤ 180°"
        ],
        "advanced_trigonometry": [
            "Express 3sinθ + 4cosθ in the form Rsin(θ + α), where R > 0 and 0° < α < 90°",
            "Prove that sin3θ = 3sinθ - 4sin³θ using compound angle formulae",
            "Solve the equation 5sinθ - 12cosθ = 6 for 0° ≤ θ ≤ 360°"
        ]
    }
    
    questions = question_templates.get(topic_id, [])
    if questions:
        return questions[difficulty == "hard" if len(questions) > 1 else 0]
    return "Solve the given trigonometric problem showing all working."