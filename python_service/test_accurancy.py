import matplotlib.pyplot as plt
import numpy as np

# Data for each topic
topics = ['Identities', 'Fundamental', 'Equations']
correct_answers = [10, 9, 8]
total_questions = [10, 15, 10]

# Calculate accuracy for each topic
accuracy_percentages = []
for i in range(len(topics)):
    accuracy = (correct_answers[i] / total_questions[i]) * 100
    accuracy_percentages.append(accuracy)
    print(f"{topics[i]} Accuracy: {accuracy:.1f}% ({correct_answers[i]}/{total_questions[i]})")

# Calculate overall accuracy
total_correct = sum(correct_answers)
total_questions_all = sum(total_questions)
overall_accuracy = (total_correct / total_questions_all) * 100

print(f"\nOverall Accuracy: {overall_accuracy:.1f}% ({total_correct}/{total_questions_all})")

# Create bar graph
plt.figure(figsize=(10, 6))
bars = plt.bar(topics, accuracy_percentages, color=['#FF6B6B', '#4ECDC4', '#45B7D1'], alpha=0.8)

# Add overall accuracy as a horizontal line
plt.axhline(y=overall_accuracy, color='red', linestyle='--', linewidth=2, label=f'Overall Accuracy: {overall_accuracy:.1f}%')

# Customize the graph
plt.title('Sinewise Trig Tutor - Accuracy by Topic', fontsize=14, fontweight='bold')
plt.ylabel('Accuracy (%)', fontsize=12)
plt.xlabel('Topics', fontsize=12)
plt.ylim(0, 100)

# Add value labels on top of each bar
for bar, accuracy in zip(bars, accuracy_percentages):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{accuracy:.1f}%', ha='center', va='bottom', fontweight='bold')

# Add legend and grid
plt.legend()
plt.grid(axis='y', alpha=0.3)

# Display the graph
plt.tight_layout()
plt.show()

# Additional detailed output
print("\n" + "="*50)
print("DETAILED BREAKDOWN:")
print("="*50)
for i in range(len(topics)):
    print(f"{topics[i]}:")
    print(f"  Correct: {correct_answers[i]}")
    print(f"  Total: {total_questions[i]}")
    print(f"  Accuracy: {accuracy_percentages[i]:.1f}%")
    print()

print(f"OVERALL SUMMARY:")
print(f"Total Correct: {total_correct}")
print(f"Total Questions: {total_questions_all}")
print(f"Overall Accuracy: {overall_accuracy:.1f}%")