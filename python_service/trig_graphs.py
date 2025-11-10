import matplotlib.pyplot as plt
import numpy as np
import io
import re
import json
import math

# Load dataset (with all graph data you provided)
def load_dataset():
    try:
        with open("trig_dataset.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ Dataset not found.")
        return []

dataset = load_dataset()

# ---------------------------
# 1️⃣ Find question in dataset
# ---------------------------
# In trig_graphs.py, update the find_dataset_graph function:

def find_dataset_graph(question):
    """Find matching graph in dataset - FIXED VERSION"""
    if not dataset or not isinstance(dataset, list):
        return None
        
    question_lower = question.lower()
    
    for item in dataset:
        # Skip if item is not a dictionary
        if not isinstance(item, dict):
            continue
            
        item_question = item.get("question", "")
        if not isinstance(item_question, str):
            continue
            
        item_question_lower = item_question.lower()
        
        # Check if this is a graph-related question
        if "graph" in item_question_lower or "sketch" in item_question_lower:
            # Match based on function name (sin, cos, tan)
            if any(func in question_lower for func in ["sin", "cos", "tan"]):
                plotting_instructions = item.get("plotting_instructions", {})
                if isinstance(plotting_instructions, dict):
                    equation = plotting_instructions.get("equation", "").lower()
                    if equation and any(func in equation for func in ["sin", "cos", "tan"]):
                        return item
    return None


# ---------------------------
# 2️⃣ Execute dataset matplotlib code
# ---------------------------
def execute_matplotlib_code(code):
    plt.close("all")  # reset current figure
    namespace = {"plt": plt, "np": np, "math": math}
    try:
        exec(code, namespace)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print("❌ Error executing matplotlib code:", e)
        return None


# ---------------------------
# 3️⃣ FIXED Equation Parser - Handles Phase Shifts
# ---------------------------
def parse_trig_equation(equation):
    """
    Fixed parser that correctly handles phase shifts:
    - sin(x), cos(x), tan(x)
    - 2sin(x), 3cos(2x), -sin(x)
    - sin(x-1), cos(x+2), tan(x-π/4)
    - sin(2x-1), cos(3x+2), etc.
    - sin(x)+1, cos(x)-2, 2sin(x)+3
    """
    # Clean the equation
    expr = equation.lower().replace("y=", "").replace(" ", "").replace("^", "**")
    
    print(f"🔍 Parsing equation: {equation}")
    print(f"🔍 Cleaned expression: {expr}")
    
    # Determine function type
    if "sin" in expr:
        func_type = "sin"
        func_str = "sin"
    elif "cos" in expr:
        func_type = "cos"
        func_str = "cos"
    elif "tan" in expr:
        func_type = "tan"
        func_str = "tan"
    else:
        raise ValueError("Equation must contain sin, cos, or tan.")
    
    # Default parameters
    a = 1  # amplitude
    b = 1  # frequency
    c = 0  # vertical shift
    d = 0  # phase shift
    
    # Extract amplitude (a) - before the function
    amp_pattern = r'^([+-]?\d*\.?\d*)\*?' + func_str
    amp_match = re.search(amp_pattern, expr)
    if amp_match and amp_match.group(1):
        amp_str = amp_match.group(1)
        if amp_str in ['', '+']:
            a = 1
        elif amp_str == '-':
            a = -1
        else:
            a = float(amp_str)
    
    # Extract the inner content of the function
    inner_pattern = func_str + r'\(([^)]+)\)'
    inner_match = re.search(inner_pattern, expr)
    
    if inner_match:
        inner_content = inner_match.group(1)
        print(f"🔍 Inner content: {inner_content}")
        
        # Handle different inner content formats
        if 'x' in inner_content:
            # Cases like: x, 2x, 3x-1, x+2, etc.
            if inner_content == 'x':
                b = 1
                d = 0
            else:
                # Extract frequency coefficient before x
                freq_match = re.search(r'([+-]?\d*\.?\d*)\s*x', inner_content)
                if freq_match:
                    freq_str = freq_match.group(1)
                    if freq_str in ['', '+']:
                        b = 1
                    elif freq_str == '-':
                        b = -1
                    else:
                        b = float(freq_str)
                
                # Extract phase shift after x
                phase_match = re.search(r'x\s*([+-])\s*(\d*\.?\d*)', inner_content)
                if phase_match:
                    sign = 1 if phase_match.group(1) == '+' else -1
                    d = sign * float(phase_match.group(2))
                    print(f"🔍 Found phase shift: {d}")
        else:
            # Case like: sin(1) - treat as constant phase shift
            try:
                d = float(inner_content)
                b = 0  # No x term, so frequency is 0
            except:
                d = 0
    
    # Extract vertical shift (c) - outside the function
    # Remove the function part to find remaining terms
    func_part_pattern = r'([+-]?\d*\.?\d*)\*?' + func_str + r'\([^)]+\)'
    func_part_match = re.search(func_part_pattern, expr)
    
    if func_part_match:
        remaining = expr.replace(func_part_match.group(0), "")
        if remaining:
            # Look for +number or -number
            shift_match = re.search(r'([+-])(\d*\.?\d*)$', remaining)
            if shift_match:
                sign = 1 if shift_match.group(1) == '+' else -1
                c = sign * float(shift_match.group(2))
    
    print(f"✅ Parsed: {equation} -> {func_type}, a={a}, b={b}, c={c}, d={d}")
    return func_type, a, b, c, d


def generate_custom_graph(equation, use_radians=False):
    """
    Generates professional trigonometric graphs with key points
    """
    plt.close("all")
    
    try:
        # Parse the equation
        func_type, a, b, c, d = parse_trig_equation(equation)
        
        print(f"📊 Generating graph for: {equation}")
        print(f"📈 Parameters: func={func_type}, amplitude={a}, frequency={b}, vertical_shift={c}, phase_shift={d}")
        
        # Determine appropriate x-range
        if use_radians:
            x_min, x_max = -2*np.pi, 2*np.pi
            x = np.linspace(x_min, x_max, 400)
            x_label = "x (radians)"
            # For phase shifts in radians, adjust the x-range
            if d != 0:
                x_min, x_max = -2*np.pi + d, 2*np.pi + d
                x = np.linspace(x_min, x_max, 400)
        else:
            x_min, x_max = -360, 360
            x = np.linspace(x_min, x_max, 400)
            x_label = "x (degrees)"
            # For phase shifts in degrees, adjust the x-range
            if d != 0:
                x_min, x_max = -360 + d, 360 + d
                x = np.linspace(x_min, x_max, 400)
        
        # Convert to radians if using degrees for calculation
        if use_radians:
            x_calc = x
            phase_shift_rad = d
        else:
            x_calc = np.radians(x)
            phase_shift_rad = np.radians(d)
        
        # Calculate y values with proper phase shift
        if func_type == "sin":
            y = a * np.sin(b * x_calc + phase_shift_rad) + c
        elif func_type == "cos":
            y = a * np.cos(b * x_calc + phase_shift_rad) + c
        elif func_type == "tan":
            y = a * np.tan(b * x_calc + phase_shift_rad) + c
            # Handle asymptotes for tangent
            y = np.clip(y, -10, 10)  # Limit extreme values
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot the main function
        ax.plot(x, y, "b-", linewidth=2, label=f"y = {equation.replace('y=', '').strip()}")
        
        # Add grid and axes
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.axhline(y=0, color="k", linewidth=0.8)
        ax.axvline(x=0, color="k", linewidth=0.8)
        
        # Set labels and title
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel("y", fontsize=12)
        title = f"Graph of y = {equation.replace('y=', '').strip()}"
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Add midline
        if c != 0:
            ax.axhline(y=c, color='orange', linestyle='--', alpha=0.7, label=f'Midline y={c}')
        
        # Plot key points
        plot_key_points(ax, func_type, a, b, c, d, x, y, use_radians)
        
        # Add legend
        ax.legend(loc='upper right', framealpha=0.9)
        
        # Set appropriate y-limits
        if func_type == "tan":
            ax.set_ylim(-8, 8)
        else:
            y_margin = abs(a) * 0.2
            ax.set_ylim(c - abs(a) - y_margin, c + abs(a) + y_margin)
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.getvalue()
        
    except Exception as e:
        print(f"❌ Error generating graph: {e}")
        import traceback
        traceback.print_exc()
        return None

def plot_key_points(ax, func_type, a, b, c, d, x, y, use_radians):
    """
    Plot key points on the graph
    """
    try:
        # Plot y-intercept
        x_zero = 0
        if use_radians:
            x_calc = 0
        else:
            x_calc = np.radians(0)
        
        if func_type == "sin":
            y_zero = a * np.sin(b * x_calc + (np.radians(d) if not use_radians else d)) + c
        elif func_type == "cos":
            y_zero = a * np.cos(b * x_calc + (np.radians(d) if not use_radians else d)) + c
        elif func_type == "tan":
            y_zero = a * np.tan(b * x_calc + (np.radians(d) if not use_radians else d)) + c
        
        ax.plot([0], [y_zero], 'ro', markersize=6, label=f'y-intercept ({y_zero:.2f})', zorder=5)
        
        # For phase shifted functions, show the shift
        if d != 0:
            # Find where the function crosses the midline for sin/cos
            if func_type in ["sin", "cos"]:
                if use_radians:
                    shift_x = -d/b if b != 0 else 0
                else:
                    shift_x = -d/b if b != 0 else 0
                
                if min(x) <= shift_x <= max(x):
                    if func_type == "sin":
                        shift_y = a * np.sin(b * (np.radians(shift_x) if not use_radians else shift_x) + (np.radians(d) if not use_radians else d)) + c
                    else:
                        shift_y = a * np.cos(b * (np.radians(shift_x) if not use_radians else shift_x) + (np.radians(d) if not use_radians else d)) + c
                    
                    ax.axvline(x=shift_x, color='purple', linestyle=':', alpha=0.7, label=f'Phase shift x={shift_x:.1f}')
                    
    except Exception as e:
        print(f"⚠️ Error plotting key points: {e}")


# ---------------------------
# 4️⃣ TEST FUNCTION for phase shifts
# ---------------------------
def test_phase_shift_parsing():
    """
    Test the parser with phase shift equations
    """
    test_cases = [
        "sin(x)",
        "sin(x-1)",
        "sin(x+2)",
        "cos(x-1)", 
        "2sin(x-1)",
        "sin(2x-1)",
        "cos(x)+1",
        "sin(x-1)+2"
    ]
    
    print("🧪 Testing Phase Shift Parser:")
    print("-" * 50)
    
    for equation in test_cases:
        try:
            func_type, a, b, c, d = parse_trig_equation(equation)
            print(f"✅ '{equation}' -> {func_type}, a={a}, b={b}, c={c}, d={d}")
        except Exception as e:
            print(f"❌ '{equation}' -> ERROR: {e}")


# ---------------------------
# 5️⃣ Unified Function
# ---------------------------
def generate_graph_for_question(question):
    """
    First tries to match dataset-based graph questions.
    If not found, uses custom dynamic graph generation.
    """
    # Step 1: Check dataset
    item = find_dataset_graph(question)
    if item and "matplotlib_code" in item:
        print(f"✅ Found dataset-based graph for: {item['topic']}")
        return execute_matplotlib_code(item["matplotlib_code"])
    
    # Step 2: Extract equation from question or use question as equation
    equation = question
    
    # Try to extract just the equation part if it's a full sentence
    if ":" in question:
        # Cases like "Graph the function: sin(x-1)"
        parts = question.split(":")
        if len(parts) > 1:
            equation = parts[1].strip()
    
    # Also try to extract equation after "y="
    if "y=" in question.lower():
        match = re.search(r'y\s*=\s*[^\.\?\!]+', question, re.IGNORECASE)
        if match:
            equation = match.group(0)
    
    # Step 3: Determine if using radians or degrees
    use_radians = "radian" in question.lower() or "π" in question
    
    print(f"🎯 Generating graph for equation: '{equation}' (radians: {use_radians})")
    
    # Step 4: Fallback to dynamic equation plotting
    return generate_custom_graph(equation, use_radians)
# Run tests if this file is executed directly
if __name__ == "__main__":
    test_phase_shift_parsing()