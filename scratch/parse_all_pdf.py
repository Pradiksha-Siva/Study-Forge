import os
import re
import json
import pypdf

def main():
    pdf_path = r"C:\Users\Pradiksha sivakumar\.gemini\antigravity\brain\fd989da7-3ad1-42a4-a549-b4ad03515e02\media__1782571886682.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return
        
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    questions = []
    current_q_num = None
    current_q_text = None
    current_ans_lines = []
    
    # We want to skip headers/footers
    skip_patterns = [
        re.compile(r"^240 CORE JAVA INTERVIEW QUESTIONS & ANSWERS$", re.IGNORECASE),
        re.compile(r"^Core Java Interview Prep$", re.IGNORECASE),
        re.compile(r"^Page \d+$", re.IGNORECASE),
        re.compile(r"^CODING STANDARDS$", re.IGNORECASE),
        re.compile(r"^EXCEPTION HANDLING$", re.IGNORECASE),
        re.compile(r"^MULTITHREADING$", re.IGNORECASE),
        re.compile(r"^NESTED & INNER CLASSES$", re.IGNORECASE),
        re.compile(r"^OOP CONCEPTS$", re.IGNORECASE),
        re.compile(r"^COLLECTIONS FRAMEWORK$", re.IGNORECASE),
        re.compile(r"^SERIALIZATION$", re.IGNORECASE)
    ]
    
    def should_skip(line):
        stripped = line.strip()
        if not stripped:
            return True
        for pattern in skip_patterns:
            if pattern.match(stripped):
                return True
        return False

    # Extract all text page-by-page from page 8 (index 7) to page 60 (index 59)
    for p_idx in range(7, total_pages):
        page_text = reader.pages[p_idx].extract_text()
        lines = page_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Check if this line is just a question number
            if stripped.isdigit() and 1 <= int(stripped) <= 240:
                # Save previous question if exists
                if current_q_num is not None and current_q_text:
                    questions.append({
                        "number": current_q_num,
                        "question": current_q_text,
                        "answer": " ".join(current_ans_lines).strip()
                    })
                
                current_q_num = int(stripped)
                current_q_text = None
                current_ans_lines = []
                
                # The next non-skipped line should be the question text
                i += 1
                while i < len(lines) and should_skip(lines[i]):
                    i += 1
                if i < len(lines):
                    current_q_text = lines[i].strip()
            else:
                if not should_skip(line):
                    current_ans_lines.append(line.strip())
            i += 1
            
    # Append the last question
    if current_q_num is not None and current_q_text:
        questions.append({
            "number": current_q_num,
            "question": current_q_text,
            "answer": " ".join(current_ans_lines).strip()
        })
        
    print(f"Total questions parsed: {len(questions)}")
    
    # Save to a JSON file
    output_path = r"C:\Users\Pradiksha sivakumar\.gemini\antigravity\scratch\StudyForge\scratch\extracted_questions.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=4)
    print(f"Questions written to {output_path}")

if __name__ == '__main__':
    main()
