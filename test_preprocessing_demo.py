#!/usr/bin/env python3
"""
Demo script to show how text preprocessing with stop word removal works
"""
from app.utils.text_preprocessing import preprocess_resume_text, get_preprocessor

# Sample resume text
sample_resume = """
John Doe
Software Engineer
Email: john.doe@email.com | Phone: (123) 456-7890

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years of experience in full-stack development. 
Proficient in JavaScript, Python, and React.js. Strong problem-solving skills and a 
passion for creating efficient, scalable applications.

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, TypeScript, Java, C++
- Frontend: React.js, Vue.js, HTML, CSS, Bootstrap
- Backend: Node.js, Django, Flask, ASP.NET
- Databases: MySQL, PostgreSQL, MongoDB
- Tools: Git, Docker, AWS, Jenkins

WORK EXPERIENCE
Senior Developer at Tech Company (2020-2023)
- Developed and maintained web applications using React and Node.js
- Collaborated with the team to design RESTful APIs
- Implemented CI/CD pipelines with Jenkins and Docker
- Worked with stakeholders to gather requirements

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2015-2019)
GPA: 3.8/4.0
"""

print("=" * 80)
print("PREPROCESSING DEMONSTRATION")
print("=" * 80)

# Get preprocessor instance
preprocessor = get_preprocessor()

print("\n📋 CURRENT STOP WORDS LIST:")
print("-" * 80)
print(f"Total stop words: {len(preprocessor.stop_words)}")
print(f"Stop words: {sorted(preprocessor.stop_words)}")

print("\n📋 PRESERVED TECHNICAL TERMS:")
print("-" * 80)
print(f"Total preserved terms: {len(preprocessor.preserve_terms)}")
print(f"Sample preserved terms: {sorted(list(preprocessor.preserve_terms))[:20]}")

print("\n\n" + "=" * 80)
print("ORIGINAL TEXT (first 500 chars):")
print("=" * 80)
print(sample_resume[:500])

print("\n\n" + "=" * 80)
print("PREPROCESSED TEXT (Standard):")
print("=" * 80)
preprocessed_standard = preprocess_resume_text(sample_resume, for_matching=False)
print(preprocessed_standard[:500])

print("\n\n" + "=" * 80)
print("PREPROCESSED TEXT (For Matching - with stop word removal):")
print("=" * 80)
preprocessed_matching = preprocess_resume_text(sample_resume, for_matching=True)
print(preprocessed_matching[:500])

print("\n\n" + "=" * 80)
print("COMPARISON:")
print("=" * 80)
original_words = sample_resume.split()
preprocessed_words = preprocessed_matching.split()

print(f"Original word count: {len(original_words)}")
print(f"Preprocessed word count: {len(preprocessed_words)}")
print(f"Words removed: {len(original_words) - len(preprocessed_words)}")
print(f"Reduction: {((len(original_words) - len(preprocessed_words)) / len(original_words) * 100):.1f}%")

print("\n\n" + "=" * 80)
print("EXAMPLES OF STOP WORDS REMOVED:")
print("=" * 80)
sample_text = "I have experience in the field of software development and I am proficient with Python"
preprocessed_sample = preprocess_resume_text(sample_text, for_matching=True)
print(f"Before: {sample_text}")
print(f"After:  {preprocessed_sample}")

print("\n" + "=" * 80)
print("TECHNICAL TERMS PRESERVATION:")
print("=" * 80)
tech_text = "Experienced with react.js, node.js, c++, and asp.net"
preprocessed_tech = preprocess_resume_text(tech_text, for_matching=False)
print(f"Before: {tech_text}")
print(f"After:  {preprocessed_tech}")

print("\n\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
