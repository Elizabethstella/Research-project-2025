// src/utils/topicDetection.js

export function detectTopicFromQuestion(question) {
  if (!question || typeof question !== 'string') {
    return "trigonometric_identities"; // default fallback
  }

  const q = question.toLowerCase().trim();
  
  // Trigonometric Identities
  if (q.includes('prove') || q.includes('identity') || q.includes('identities') || 
      q.match(/sin\s*\(.*\)|cos\s*\(.*\)|tan\s*\(.*\)/) ||
      q.includes('pythagorean')) {
    return "trigonometric_identities";
  }
  
  // Trigonometric Graphs
  else if (q.includes('graph') || q.includes('sketch') || q.includes('plot') ||
           q.includes('amplitude') || q.includes('period') || q.includes('frequency') ||
           q.includes('wavelength') || q.includes('phase') || q.includes('shift') ||
           q.includes('sine wave') || q.includes('cosine wave')) {
    return "trigonometric_graphs";
  }
  
  // Trigonometric Equations
  else if (q.includes('solve') || q.includes('equation') || q.includes('solution') ||
           q.includes('find x') || q.includes('value of') || q.includes('root') ||
           q.includes('θ') || q.includes('theta')) {
    return "trigonometric_equations";
  }
  
  // Circular Measure
  else if (q.includes('radian') || q.includes('arc') || q.includes('sector') || 
           q.includes('segment') || q.includes('circle') || q.includes('circular') ||
           q.includes('angle') || q.includes('degree') || q.includes('π') ||
           q.includes('pi') || q.includes('circumference')) {
    return "circular_measure";
  }
  
  // Advanced Trigonometry
  else if (q.includes('sec') || q.includes('csc') || q.includes('cot') || 
           q.includes('cosec') || q.includes('cotangent') ||
           q.includes('compound') || q.includes('double angle') || q.includes('half angle') ||
           q.includes('addition') || q.includes('subtraction') || q.includes('formula') ||
           q.includes('sin(a+b)') || q.includes('cos(a+b)') || q.includes('r formula') ||
           q.includes('r-formula') || q.includes('harmonic')) {
    return "advanced_trigonometry";
  }
  
  // Basic Trigonometry (fallback for basic questions)
  else if (q.includes('sin') || q.includes('cos') || q.includes('tan') || 
           q.includes('trig') || q.includes('triangle') || q.includes('right angle')) {
    return "trigonometric_functions";
  }
  
  else {
    return "trigonometric_identities"; // default fallback
  }
}

// Optional: Export a function to get topic display name
export function getTopicDisplayName(topicId) {
  const topicMap = {
    "trigonometric_identities": "Trigonometric Identities",
    "trigonometric_graphs": "Trigonometric Graphs", 
    "trigonometric_equations": "Trigonometric Equations",
    "circular_measure": "Circular Measure",
    "advanced_trigonometry": "Advanced Trigonometry",
    "trigonometric_functions": "Trigonometric Functions"
  };
  
  return topicMap[topicId] || "Trigonometry";
}