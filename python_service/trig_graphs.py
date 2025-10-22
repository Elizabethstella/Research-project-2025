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
def find_dataset_graph(question):
    question_lower = question.lower()
    for item in dataset:
        if "graph" in item.get("question", "").lower() or "sketch" in item.get("question", "").lower():
            # Match based on function name (sin, cos, tan)
            if any(func in question_lower for func in ["sin", "cos", "tan"]):
                equation = item["plotting_instructions"].get("equation", "").lower()
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
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print("❌ Error executing matplotlib code:", e)
        return None


# ---------------------------
# 3️⃣ Dynamic Graph Generation (custom input)
# ---------------------------
def generate_custom_graph(equation):
    """
    Generates graph dynamically for equations like:
    y = sin(x), y = 2sin(3x)+1, y = a cos(bx)+c, etc.
    """
    plt.close("all")
    try:
        # Clean and parse the equation
        expr = equation.lower().replace("y=", "").replace(" ", "")
        func_type = "sin" if "sin" in expr else "cos" if "cos" in expr else "tan" if "tan" in expr else None

        if not func_type:
            raise ValueError("Equation must contain sin, cos, or tan.")

        # Extract coefficients a, b, and c from y = a*sin(bx) + c
        a = 1
        b = 1
        c = 0

        # Match amplitude (a)
        amp_match = re.match(r"(\d*\.?\d*)", expr)
        if amp_match and amp_match.group(1):
            a = float(amp_match.group(1))

        # Match frequency (b)
        freq_match = re.search(r"[a-z]\((\d*\.?\d*)x\)", expr)
        if freq_match and freq_match.group(1):
            b = float(freq_match.group(1))

        # Match vertical shift (c)
        shift_match = re.search(r"\+(\d+\.?\d*)", expr)
        neg_shift_match = re.search(r"-(\d+\.?\d*)", expr)
        if shift_match:
            c = float(shift_match.group(1))
        elif neg_shift_match:
            c = -float(neg_shift_match.group(1))

        # Set x range (degrees)
        x = np.linspace(0, 360, 400)
        radians = np.radians(x)

        # Calculate y based on trig function
        if func_type == "sin":
            y = a * np.sin(b * radians) + c
        elif func_type == "cos":
            y = a * np.cos(b * radians) + c
        elif func_type == "tan":
            y = a * np.tan(b * radians) + c

        # Plot graph
        plt.figure(figsize=(10, 5))
        plt.plot(x, y, "b-", linewidth=2)
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color="k", linewidth=0.5)
        plt.axvline(x=0, color="k", linewidth=0.5)
        plt.title(f"Graph of {equation}")
        plt.xlabel("x (degrees)")
        plt.ylabel("y")

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        print(f"❌ Error generating graph dynamically: {e}")
        return None


# ---------------------------
# 4️⃣ Unified Function
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

    # Step 2: Fallback to dynamic equation plotting
    print("ℹ️ Using dynamic graph generation.")
    return generate_custom_graph(question)
