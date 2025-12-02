#!/usr/bin/env python3
"""
Test the improved stop word removal
"""
import re

# Old stop words (23 words)
old_stop_words = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'were', 'will', 'with'
}

# New expanded stop words (~150 words)
new_stop_words = {
    # Articles
    'a', 'an', 'the',
    
    # Pronouns
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
    'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
    
    # Conjunctions
    'and', 'but', 'or', 'nor', 'so', 'yet',
    
    # Prepositions
    'about', 'above', 'across', 'after', 'against', 'along', 'among',
    'around', 'as', 'at', 'before', 'behind', 'below', 'beneath',
    'beside', 'between', 'beyond', 'by', 'down', 'during', 'except',
    'for', 'from', 'in', 'inside', 'into', 'near', 'of', 'off', 'on',
    'onto', 'out', 'outside', 'over', 'through', 'throughout', 'to',
    'toward', 'under', 'underneath', 'until', 'up', 'upon', 'with',
    'within', 'without',
    
    # Common verbs
    'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'will', 'would', 'shall', 'can', 'could', 'may', 'might',
    
    # Common adjectives/adverbs
    'very', 'more', 'most', 'such', 'no', 'not', 'only', 'just',
    'too', 'also', 'than', 'then', 'there', 'here', 'when', 'where',
    'why', 'how', 'all', 'each', 'every', 'both', 'few', 'some',
    'any', 'many', 'much', 'other', 'another', 'same', 'own',
    
    # Common connecting words
    'if', 'because', 'while', 'since', 'though', 'although',
    'unless', 'whether', 'nor',
    
    # Other common words
    'get', 'got', 'make', 'made', 'now', 'way', 'even', 'well',
    'back', 'still', 'go', 'see', 'seem', 'come', 'came', 'take',
    'took', 'know', 'knew', 'think', 'thought', 'say', 'said'
}

print("=" * 80)
print("IMPROVED STOP WORD REMOVAL - COMPARISON")
print("=" * 80)

print(f"\n📊 STATISTICS:")
print("-" * 80)
print(f"Old stop words count: {len(old_stop_words)}")
print(f"New stop words count: {len(new_stop_words)}")
print(f"Improvement: +{len(new_stop_words) - len(old_stop_words)} words ({((len(new_stop_words) - len(old_stop_words)) / len(old_stop_words) * 100):.0f}% increase)")

# Sample resume text
sample_text = """
I have over 5 years of experience in software development. I am very proficient 
with Python, JavaScript, and React. I worked on many projects where I developed 
and maintained web applications. I can work well with teams and I have strong 
problem-solving skills. I also have experience with databases such as MySQL and 
PostgreSQL. I know how to use Git, Docker, and AWS. I think I would be a great 
fit for this position because I have all the required skills.
"""

print("\n\n" + "=" * 80)
print("SAMPLE RESUME TEXT:")
print("=" * 80)
print(sample_text.strip())

# Process with old stop words
words = sample_text.lower().split()
old_filtered = [w for w in words if w not in old_stop_words and len(w) > 1]
new_filtered = [w for w in words if w not in new_stop_words and len(w) > 1]

print("\n\n" + "=" * 80)
print("OLD PREPROCESSING (23 stop words):")
print("=" * 80)
print(' '.join(old_filtered))
print(f"\nOriginal: {len(words)} words")
print(f"After filtering: {len(old_filtered)} words")
print(f"Removed: {len(words) - len(old_filtered)} words ({((len(words) - len(old_filtered)) / len(words) * 100):.1f}%)")

print("\n\n" + "=" * 80)
print("NEW PREPROCESSING (~150 stop words):")
print("=" * 80)
print(' '.join(new_filtered))
print(f"\nOriginal: {len(words)} words")
print(f"After filtering: {len(new_filtered)} words")
print(f"Removed: {len(words) - len(new_filtered)} words ({((len(words) - len(new_filtered)) / len(words) * 100):.1f}%)")

print("\n\n" + "=" * 80)
print("ADDITIONAL WORDS REMOVED BY NEW PREPROCESSING:")
print("=" * 80)
additional_removed = set(old_filtered) - set(new_filtered)
print(f"Count: {len(additional_removed)}")
print(f"Words: {sorted(additional_removed)}")

print("\n\n" + "=" * 80)
print("KEY IMPROVEMENTS:")
print("=" * 80)
print("✅ Removes filler words: 'very', 'many', 'also', 'well', 'just', etc.")
print("✅ Removes pronouns: 'i', 'me', 'my', 'myself', etc.")
print("✅ Removes common verbs: 'think', 'know', 'seem', 'would', etc.")
print("✅ Still preserves: Python, JavaScript, React, MySQL, PostgreSQL, Git, Docker, AWS")
print("✅ Better focus on meaningful technical terms and skills")
print("\n🎯 Result: More focused matching on actual skills and experience!")
print("=" * 80)
