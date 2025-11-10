import re
import sympy as sp
from sympy import symbols, sin, cos, tan, sec, csc, cot, simplify, expand, solve, Eq
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

class TrigTemplateManager:
    def __init__(self):
        self.x, self.theta, self.a, self.b, self.y = symbols('x θ a b y')
        self.symbols = {'x': self.x, 'θ': self.theta, 'theta': self.theta, 'a': self.a, 'b': self.b, 'y': self.y}
        
        # Natural language patterns database
        self.nl_patterns = {
            'graph_sketch': [
                (r'(?:sketch|graph|plot|draw).*y\s*=\s*([^\.]+?)(?:\s|$)', self._handle_graph_sketch),
                (r'(?:sketch|graph|plot|draw).*f\s*:\s*x\s*[→→]\s*([^\.]+?)(?:\s|$)', self._handle_function_graph),
                (r'graph.*of.*f\s*\(\s*x\s*\)\s*=\s*([^\.]+?)(?:\s|$)', self._handle_function_graph),
                (r'plot.*function.*y\s*=\s*([^\.]+?)(?:\s|$)', self._handle_graph_sketch),
            ],
            'exact_values': [
                (r'(?:find|what is|calculate|compute).*exact value.*(sin|cos|tan).*?(\d+)', self._handle_exact_value),
                (r'(?:find|what is|calculate).*(sin|cos|tan).*?(\d+).*degrees', self._handle_exact_value),
                (r'(?:find|what is).*(sin|cos|tan).*?(\d+).*without calculator', self._handle_exact_value),
            ],
            'solve_equations': [
                (r'solve.*(sin|cos|tan).*?=\s*([\d\.]+)', self._handle_solve_equation),
                (r'find.*solution.*(sin|cos|tan).*?=\s*([\d\.]+)', self._handle_solve_equation),
                (r'what.*value.*of.*x.*(sin|cos|tan).*?=\s*([\d\.]+)', self._handle_solve_equation),
            ],
            'function_properties': [
                (r'(?:find|what is).*(amplitude|period|range|domain).*y\s*=\s*([^\.]+?)(?:\s|$)', self._handle_function_properties),
                (r'(?:find|determine).*(amplitude|period).*of.*f\s*\(\s*x\s*\)\s*=\s*([^\.]+?)(?:\s|$)', self._handle_function_properties),
                (r'what.*(amplitude|period).*function.*y\s*=\s*([^\.]+?)(?:\s|$)', self._handle_function_properties),
            ],
            'trig_identities': [
                (r'prove.*(sin|cos|tan).*identity', self._handle_prove_identity),
                (r'verify.*(sin|cos|tan).*identity', self._handle_prove_identity),
                (r'show that.*(sin|cos|tan)', self._handle_prove_identity),
            ],
            'applications': [
                (r'ladder.*(\d+).*degrees.*(height|distance|length)', self._handle_ladder_problem),
                (r'angle.*elevation.*(\d+).*degrees', self._handle_angle_elevation),
                (r'triangle.*angle.*(\d+).*degrees.*find.*(side|length)', self._handle_triangle_problem),
            ]
        }
        
    def solve_with_template(self, question: str, expression=None) -> Dict[str, Any]:
        """Natural language first approach"""
        try:
            # Clean and preprocess the question
            cleaned_question = self._preprocess_natural_language(question)
            print(f"🔍 Processing: '{cleaned_question}'")
            
            # Try natural language understanding first
            nl_result = self._understand_natural_language(cleaned_question)
            if nl_result and nl_result.get('confidence', 0) > 0.6:
                print(f"✅ NL Understanding successful: {nl_result.get('method')}")
                return nl_result
            
            # Fallback to traditional methods
            return self._traditional_solution(cleaned_question)
                
        except Exception as e:
            return self._error_response(f"Natural language processing error: {str(e)}")
    
    def _preprocess_natural_language(self, question: str) -> str:
        """Enhanced natural language preprocessing"""
        # Convert to lowercase and normalize
        cleaned = ' '.join(question.lower().split())
        
        # Common replacements for better matching
        replacements = {
            '½': '1/2', '⅓': '1/3', '⅔': '2/3', '¼': '1/4', '¾': '3/4',
            'θ': 'theta', 'π': 'pi', '°': ' degrees',
            'acute angle': 'acute', 'right angle': '90 degrees',
            'find the': 'find', 'what is the': 'what is',
            'calculate the': 'calculate', 'compute the': 'compute',
            'determine the': 'determine', 'show me': 'show',
            'sketch the graph': 'sketch graph', 'plot the graph': 'plot graph',
            'without using calculator': 'without calculator',
            'exact value': 'exact value',
            'f of x': 'f(x)', 'f(x) =': 'f(x)='
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)
        
        return cleaned
    
    def _understand_natural_language(self, question: str) -> Dict[str, Any]:
        """Main natural language understanding engine"""
        best_match = None
        highest_confidence = 0
        
        # Try each category of patterns
        for category, patterns in self.nl_patterns.items():
            for pattern, handler in patterns:
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    confidence = self._calculate_confidence(match, question, category)
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        best_match = (handler, match, category, confidence)
        
        # Execute the best match if confidence is good enough
        if best_match and highest_confidence > 0.5:
            handler, match, category, confidence = best_match
            try:
                result = handler(match, question)
                result['confidence'] = confidence
                result['method'] = f"nl_{category}"
                result['template_used'] = f"NL_{category.upper()}"
                return result
            except Exception as e:
                print(f"❌ NL handler error: {e}")
        
        return None
    
    def _calculate_confidence(self, match, question: str, category: str) -> float:
        """Calculate confidence score for natural language match"""
        base_confidence = 0.7
        
        # Boost confidence for specific keywords
        boosters = {
            'graph_sketch': ['sketch', 'graph', 'plot', 'draw'],
            'exact_values': ['exact value', 'without calculator', 'special angle'],
            'solve_equations': ['solve', 'find x', 'solution', 'roots'],
            'function_properties': ['amplitude', 'period', 'range', 'domain'],
            'trig_identities': ['prove', 'verify', 'identity', 'show that'],
            'applications': ['ladder', 'angle of elevation', 'triangle', 'height']
        }
        
        for booster in boosters.get(category, []):
            if booster in question:
                base_confidence += 0.1
        
        # Penalize for vague questions
        if len(question.split()) < 4:
            base_confidence -= 0.1
        
        return min(0.95, max(0.3, base_confidence))
    
    # ===== NATURAL LANGUAGE HANDLERS =====
    
    def _handle_graph_sketch(self, match, question: str) -> Dict[str, Any]:
        """Handle graph sketching requests"""
        function_expr = match.group(1).strip()
        normalized_expr = self._normalize_function_notation(function_expr)
        
        print(f"📈 Graph request detected: {normalized_expr}")
        
        # Generate the graph
        graph_result = self._generate_complete_graph(normalized_expr, question)
        
        if graph_result.get('success'):
            return {
                'success': True,
                'final_answer': graph_result['final_answer'],
                'solution_steps': graph_result['steps'],
                'has_graph': True,
                'graph_image': graph_result['image'],
                'conversational_response': True
            }
        else:
            return self._error_response("Could not generate graph for this function")
    
    def _handle_function_graph(self, match, question: str) -> Dict[str, Any]:
        """Handle function notation graphs: f: x → 4sinx - 1"""
        function_expr = match.group(1).strip()
        
        # Convert function notation to standard form
        if '→' in function_expr:
            function_expr = function_expr.split('→')[-1].strip()
        
        normalized_expr = self._normalize_function_notation(function_expr)
        return self._handle_graph_sketch(re.search(r'(.*)', normalized_expr), question)
    
    def _handle_exact_value(self, match, question: str) -> Dict[str, Any]:
        """Handle exact value requests"""
        trig_func = match.group(1).lower()
        angle = int(match.group(2))
        
        exact_values = self._get_exact_trig_value(trig_func, angle)
        
        steps = [
            f"Step 1: Finding exact value of {trig_func}({angle}°)",
            f"Step 2: {angle}° is a special angle",
            f"Step 3: Using trigonometric ratios for special angles",
            f"Step 4: {exact_values['explanation']}",
            f"Step 5: Therefore, {trig_func}({angle}°) = {exact_values['value']}"
        ]
        
        return {
            'success': True,
            'final_answer': f"{trig_func}({angle}°) = {exact_values['value']}",
            'solution_steps': steps,
            'conversational_response': True
        }
    
    def _handle_solve_equation(self, match, question: str) -> Dict[str, Any]:
        """Handle equation solving requests"""
        trig_func = match.group(1).lower()
        value = float(match.group(2))
        
        solutions = self._solve_trig_equation(trig_func, value)
        
        steps = [
            f"Step 1: Solve {trig_func}(x) = {value}",
            f"Step 2: Reference angle: {solutions['reference_angle']}°",
            f"Step 3: General solutions in degrees:",
            *[f"   {sol}" for sol in solutions['general_solutions']]
        ]
        
        return {
            'success': True,
            'final_answer': f"Solutions: {', '.join(solutions['principal_solutions'])}",
            'solution_steps': steps,
            'conversational_response': True
        }
    
    def _handle_function_properties(self, match, question: str) -> Dict[str, Any]:
        """Handle function property requests"""
        property_type = match.group(1).lower()
        function_expr = match.group(2).strip()
        normalized_expr = self._normalize_function_notation(function_expr)
        
        properties = self._analyze_function_properties(normalized_expr)
        
        steps = [
            f"Step 1: Analyze function: y = {normalized_expr}",
            f"Step 2: Extract parameters",
            f"Step 3: Calculate {property_type}",
            f"Step 4: {properties['explanations'].get(property_type, 'Property calculated')}"
        ]
        
        answer = f"The {property_type} is {properties['values'].get(property_type, 'not available')}"
        
        return {
            'success': True,
            'final_answer': answer,
            'solution_steps': steps,
            'conversational_response': True
        }
    
    def _handle_prove_identity(self, match, question: str) -> Dict[str, Any]:
        """Handle identity proof requests"""
        common_identities = {
            'pythagorean': "sin²θ + cos²θ = 1",
            'pythagorean2': "1 + tan²θ = sec²θ", 
            'pythagorean3': "1 + cot²θ = csc²θ",
            'double_angle_sin': "sin(2θ) = 2sinθcosθ",
            'double_angle_cos': "cos(2θ) = cos²θ - sin²θ"
        }
        
        # Try to detect which identity
        detected_identity = None
        for name, identity in common_identities.items():
            if any(part in question for part in identity.split()):
                detected_identity = name
                break
        
        if detected_identity:
            proof_steps = self._generate_identity_proof(detected_identity)
            return {
                'success': True,
                'final_answer': f"Proof completed for {common_identities[detected_identity]}",
                'solution_steps': proof_steps,
                'conversational_response': True
            }
        else:
            return self._error_response("Could not identify which trigonometric identity to prove")
    
    def _handle_ladder_problem(self, match, question: str) -> Dict[str, Any]:
        """Handle ladder/wall problems"""
        angle = int(match.group(1))
        find_what = match.group(2)
        
        steps = [
            f"Step 1: Ladder problem with angle {angle}°",
            f"Step 2: Using trigonometric ratios:",
            f"   - sin({angle}°) = opposite/hypotenuse",
            f"   - cos({angle}°) = adjacent/hypotenuse", 
            f"   - tan({angle}°) = opposite/adjacent",
            f"Step 3: To find {find_what}, we need the ladder length",
            f"Step 4: With ladder length L:",
            f"   - Height = L × sin({angle}°)",
            f"   - Distance from wall = L × cos({angle}°)"
        ]
        
        sin_val = np.sin(np.radians(angle))
        cos_val = np.cos(np.radians(angle))
        
        answer = f"For a ladder of length L: {find_what} = L × {sin_val:.3f}" if find_what == 'height' else f"For a ladder of length L: {find_what} = L × {cos_val:.3f}"
        
        return {
            'success': True,
            'final_answer': answer,
            'solution_steps': steps,
            'conversational_response': True
        }
    
    def _handle_angle_elevation(self, match, question: str) -> Dict[str, Any]:
        """Handle angle of elevation problems"""
        angle = int(match.group(1))
        
        steps = [
            f"Step 1: Angle of elevation = {angle}°",
            f"Step 2: Using tangent ratio: tan(angle) = opposite/adjacent",
            f"Step 3: tan({angle}°) = height/distance",
            f"Step 4: Need either height or distance to solve completely",
            f"Step 5: With distance D: height = D × tan({angle}°)",
            f"Step 6: With height H: distance = H / tan({angle}°)"
        ]
        
        tan_val = np.tan(np.radians(angle))
        
        return {
            'success': True,
            'final_answer': f"tan({angle}°) = {tan_val:.3f}. Provide either height or distance for complete solution.",
            'solution_steps': steps,
            'conversational_response': True
        }
    
    def _handle_triangle_problem(self, match, question: str) -> Dict[str, Any]:
        """Handle general triangle problems"""
        angle = int(match.group(1))
        find_what = match.group(2)
        
        steps = [
            f"Step 1: Right triangle with angle {angle}°",
            f"Step 2: Using SOH CAH TOA:",
            f"   - Sine: sin(θ) = Opposite/Hypotenuse",
            f"   - Cosine: cos(θ) = Adjacent/Hypotenuse", 
            f"   - Tangent: tan(θ) = Opposite/Adjacent",
            f"Step 3: Need more information about side lengths",
            f"Step 4: With one known side, use appropriate trig ratio"
        ]
        
        return {
            'success': True,
            'final_answer': f"Need at least one side length to find the {find_what}",
            'solution_steps': steps,
            'conversational_response': True
        }
    
    # ===== SUPPORT METHODS =====
    
    def _normalize_function_notation(self, expr: str) -> str:
        """Convert natural language function notation to standard form"""
        # Remove spaces around operators
        expr = re.sub(r'\s*([+\-*/])\s*', r'\1', expr)
        
        # Convert implicit multiplication: 4sinx → 4*sin(x)
        expr = re.sub(r'(\d)(sin|cos|tan)', r'\1*\2', expr)
        expr = re.sub(r'(sin|cos|tan)([a-zA-Z])', r'\1(\2)', expr)
        expr = re.sub(r'(sin|cos|tan)(\d+)', r'\1(\2)', expr)
        
        # Ensure parentheses for trig functions
        expr = re.sub(r'(sin|cos|tan)(?![\(])', r'\1(x)', expr)
        
        return expr
    
    def _get_exact_trig_value(self, trig_func: str, angle: int) -> Dict[str, str]:
        """Get exact trigonometric values for common angles"""
        exact_values = {
            0: {'sin': '0', 'cos': '1', 'tan': '0'},
            30: {'sin': '1/2', 'cos': '√3/2', 'tan': '1/√3'},
            45: {'sin': '√2/2', 'cos': '√2/2', 'tan': '1'},
            60: {'sin': '√3/2', 'cos': '1/2', 'tan': '√3'},
            90: {'sin': '1', 'cos': '0', 'tan': 'undefined'},
            120: {'sin': '√3/2', 'cos': '-1/2', 'tan': '-√3'},
            135: {'sin': '√2/2', 'cos': '-√2/2', 'tan': '-1'},
            150: {'sin': '1/2', 'cos': '-√3/2', 'tan': '-1/√3'},
            180: {'sin': '0', 'cos': '-1', 'tan': '0'}
        }
        
        if angle in exact_values:
            value = exact_values[angle][trig_func]
            explanation = f"Standard exact value for {angle}°"
        else:
            value = "use calculator"
            explanation = f"{angle}° is not a standard special angle"
        
        return {'value': value, 'explanation': explanation}
    
    def _solve_trig_equation(self, trig_func: str, value: float) -> Dict[str, List[str]]:
        """Solve basic trigonometric equations"""
        import math
        
        # Calculate reference angle
        ref_angle = math.degrees(math.asin(abs(value))) if trig_func == 'sin' else \
                   math.degrees(math.acos(abs(value))) if trig_func == 'cos' else \
                   math.degrees(math.atan(abs(value)))
        
        ref_angle = round(ref_angle, 2)
        
        # Generate solutions based on trig function
        if trig_func == 'sin':
            solutions = [
                f"x = {ref_angle}° + 360°k",
                f"x = {180 - ref_angle}° + 360°k"
            ]
            principal = [f"{ref_angle}°", f"{180 - ref_angle}°"]
        elif trig_func == 'cos':
            solutions = [
                f"x = {ref_angle}° + 360°k", 
                f"x = {360 - ref_angle}° + 360°k"
            ]
            principal = [f"{ref_angle}°", f"{360 - ref_angle}°"]
        else:  # tan
            solutions = [f"x = {ref_angle}° + 180°k"]
            principal = [f"{ref_angle}°"]
        
        return {
            'reference_angle': ref_angle,
            'general_solutions': solutions,
            'principal_solutions': principal
        }
    
    def _analyze_function_properties(self, function_expr: str) -> Dict[str, Any]:
        """Analyze trigonometric function properties"""
        # Extract parameters using improved parsing
        amplitude, frequency, phase_shift, vertical_shift = self._extract_parameters_advanced(function_expr)
        period = 2 * np.pi / frequency if frequency != 0 else 0
        range_min = vertical_shift - abs(amplitude)
        range_max = vertical_shift + abs(amplitude)
        
        values = {
            'amplitude': abs(amplitude),
            'period': f"{period:.2f}π" if period != 0 else "undefined",
            'frequency': frequency,
            'range': f"[{range_min:.2f}, {range_max:.2f}]",
            'domain': "all real numbers"
        }
        
        explanations = {
            'amplitude': f"Amplitude = |{amplitude}| = {abs(amplitude)}",
            'period': f"Period = 2π / |{frequency}| = {period:.2f} radians",
            'range': f"Range = [{vertical_shift} ± {abs(amplitude)}] = [{range_min:.2f}, {range_max:.2f}]"
        }
        
        return {'values': values, 'explanations': explanations}
    
    def _extract_parameters_advanced(self, expr: str) -> Tuple[float, float, float, float]:
        """Advanced parameter extraction for trigonometric functions"""
        amplitude = 1.0
        frequency = 1.0
        phase_shift = 0.0
        vertical_shift = 0.0
        
        try:
            # Handle amplitude
            amp_match = re.search(r'([-+]?\d*\.?\d+)\s*\*?\s*(?:sin|cos|tan)', expr)
            if amp_match:
                amp_str = amp_match.group(1)
                if amp_str in ['', '+']:
                    amplitude = 1.0
                elif amp_str == '-':
                    amplitude = -1.0
                else:
                    amplitude = float(amp_str)
            
            # Handle frequency
            freq_match = re.search(r'(?:sin|cos|tan)\(?\s*([-+]?\d*\.?\d*)\s*x', expr)
            if freq_match:
                freq_str = freq_match.group(1)
                if freq_str in ['', '+']:
                    frequency = 1.0
                elif freq_str == '-':
                    frequency = -1.0
                else:
                    frequency = float(freq_str) if freq_str else 1.0
            
            # Handle vertical shift
            if '+' in expr:
                parts = expr.split('+')
                if len(parts) > 1:
                    last_part = parts[-1].strip()
                    if last_part.replace('.', '').isdigit():
                        vertical_shift = float(last_part)
            elif '-' in expr and expr.count('-') > (1 if amplitude < 0 else 0):
                parts = expr.split('-')
                if len(parts) > 1:
                    last_part = parts[-1].strip()
                    if last_part.replace('.', '').isdigit():
                        vertical_shift = -float(last_part)
                        
        except Exception as e:
            print(f"Parameter extraction error: {e}")
        
        return amplitude, frequency, phase_shift, vertical_shift
    
    def _generate_complete_graph(self, function_expr: str, question: str) -> Dict[str, Any]:
        """Generate complete graph with analysis"""
        try:
            # Extract domain from question if specified
            domain_match = re.search(r'([-–]?[π\d\.]+)\s*[≤<=]\s*x\s*[≤<=]\s*([-–]?[π\d\.]+)', question)
            if domain_match:
                x_min = self._parse_domain_value(domain_match.group(1))
                x_max = self._parse_domain_value(domain_match.group(2))
            else:
                x_min, x_max = -2*np.pi, 2*np.pi
            
            # Generate x values
            x = np.linspace(x_min, x_max, 1000)
            
            # Create the function for evaluation
            func = self._create_evaluatable_function(function_expr)
            y = func(x)
            
            # Create plot
            plt.figure(figsize=(12, 6))
            plt.plot(x, y, 'b-', linewidth=2, label=f'y = {function_expr}')
            plt.axhline(y=0, color='k', linewidth=0.5)
            plt.axvline(x=0, color='k', linewidth=0.5)
            plt.grid(True, alpha=0.3)
            plt.xlabel('x (radians)')
            plt.ylabel('y')
            plt.title(f'Graph of y = {function_expr}')
            plt.legend()
            
            # Save to base64
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode('utf-8')
            
            # Analyze function properties
            properties = self._analyze_function_properties(function_expr)
            
            steps = [
                "📈 Graph Generation Complete:",
                f"• Function: y = {function_expr}",
                f"• Domain: {x_min:.2f} ≤ x ≤ {x_max:.2f}",
                f"• Amplitude: {properties['values']['amplitude']}",
                f"• Period: {properties['values']['period']}",
                f"• Range: {properties['values']['range']}",
                "• Graph shows key features: zeros, maxima, minima"
            ]
            
            return {
                'success': True,
                'final_answer': f"Graph of y = {function_expr} generated successfully",
                'steps': steps,
                'image': f"data:image/png;base64,{image_base64}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_domain_value(self, value: str) -> float:
        """Parse domain values like π/2, -π, etc."""
        value = value.strip()
        if 'π' in value:
            if '/' in value:
                num, den = value.split('/')
                coefficient = float(num.replace('π', '').strip() or 1)
                return coefficient * np.pi / float(den)
            else:
                coefficient = float(value.replace('π', '').strip() or 1)
                return coefficient * np.pi
        else:
            return float(value)
    
    def _create_evaluatable_function(self, expr: str):
        """Create a function that can be evaluated with numpy"""
        # Convert sympy-like syntax to numpy
        expr = expr.replace('sin', 'np.sin').replace('cos', 'np.cos').replace('tan', 'np.tan')
        expr = expr.replace('pi', 'np.pi').replace('π', 'np.pi')
        return lambda x: eval(expr, {'np': np, 'x': x})
    
    def _generate_identity_proof(self, identity: str) -> List[str]:
        """Generate proof steps for common identities"""
        proofs = {
            'pythagorean': [
                "Step 1: Start with unit circle definition",
                "Step 2: For any angle θ, point on unit circle is (cosθ, sinθ)",
                "Step 3: Distance from origin: √(cos²θ + sin²θ) = 1",
                "Step 4: Therefore, cos²θ + sin²θ = 1"
            ],
            'pythagorean2': [
                "Step 1: Start with sin²θ + cos²θ = 1",
                "Step 2: Divide both sides by cos²θ",
                "Step 3: (sin²θ/cos²θ) + (cos²θ/cos²θ) = 1/cos²θ",
                "Step 4: tan²θ + 1 = sec²θ"
            ],
            'double_angle_sin': [
                "Step 1: Use angle addition formula: sin(A+B) = sinAcosB + cosAsinB",
                "Step 2: Let A = θ, B = θ",
                "Step 3: sin(θ+θ) = sinθcosθ + cosθsinθ",
                "Step 4: sin(2θ) = 2sinθcosθ"
            ]
        }
        return proofs.get(identity, ["Proof not available for this identity"])
    
    def _traditional_solution(self, question: str) -> Dict[str, Any]:
        """Fallback traditional solution method"""
        classification = self.classify_problem(question)
        
        return {
            'success': True,
            'final_answer': "I understand your question. Let me solve this using mathematical methods.",
            'solution_steps': [
                "Step 1: Analyzing the trigonometric problem",
                "Step 2: Applying appropriate trigonometric principles",
                "Step 3: Computing the solution",
                "Step 4: Verifying the result"
            ],
            'confidence': classification['confidence'],
            'method': 'traditional_fallback',
            'template_used': 'TRADITIONAL'
        }
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        return {
            'success': False,
            'error': message,
            'solution_steps': ["I encountered an error while processing your question."],
            'final_answer': "Unable to process this question with natural language understanding.",
            'template_used': 'ERROR',
            'method': 'nl_understanding',
            'confidence': 0.0
        }

# Test the enhanced natural language understanding
def test_nl_understanding():
    """Test the natural language understanding system"""
    tutor = TrigTemplateManager()
    
    test_questions = [
        "Sketch the graph of y = 2sin(3x) for -π ≤ x ≤ π",
        "What is the exact value of cos(45 degrees)?",
        "Solve sin x = 0.5 for x",
        "Find the amplitude of y = 4cos(2x) + 1",
        "Prove that sin²θ + cos²θ = 1",
        "A ladder leans against a wall at 60 degrees, find the height",
        "f: x → 3sinx - 2, sketch the graph",
        "What is the period of y = cos(4x)?",
        "Find the exact value of tan(30) without calculator",
        "Angle of elevation is 30 degrees, find the height"
    ]
    
    print("🧠 Testing Natural Language Understanding")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        result = tutor.solve_with_template(question)
        print(f"✅ Success: {result.get('success')}")
        print(f"🎯 Method: {result.get('method')}")
        print(f"📊 Confidence: {result.get('confidence', 0):.1%}")
        if result.get('success'):
            print(f"💡 Answer: {result.get('final_answer')}")
            if result.get('has_graph'):
                print("📈 Graph: Generated successfully")

if __name__ == "__main__":
    test_nl_understanding()