import json
import re

def main():
    log_path = r"C:\Users\Pradiksha sivakumar\.gemini\antigravity\brain\fd989da7-3ad1-42a4-a549-b4ad03515e02\.system_generated\logs\transcript_full.jsonl"
    
    # Read the first line of the transcript which contains the initial prompt with PDF OCR
    with open(log_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        
    data = json.loads(first_line)
    content = data.get('content', '')
    
    # Extract OCR pages text using a relaxed spacing pattern
    pages = re.findall(r'==Start of OCR for page (\d+)==\s*(.*?)\s*==End of OCR for page \d+==', content, re.DOTALL)
    print(f"Found {len(pages)} OCR pages.")
    
    if len(pages) == 0:
        # Let's inspect a snippet of content to see why it didn't match
        print("First 500 chars of content:")
        print(content[:500])
        return
        
    # Sort pages by page number
    pages = sorted(pages, key=lambda x: int(x[0]))
    
    # Combine pages 8 to 60
    study_text = ""
    for p_num, p_text in pages:
        if int(p_num) >= 8:
            study_text += "\n" + p_text
            
    print(f"Combined study text length: {len(study_text)}")
    
    # Regex to find questions and answers
    # Questions start with digits followed by spaces and a question body.
    # E.g. "1 What are static blocks..."
    # The next question starts with another digits followed by spaces and a capital letter.
    pattern = re.compile(r'(?:^|\n)\s*(\d+)\s+([A-Z].*?)(?=\n\s*(?:\d+)\s+[A-Z]|\Z)', re.DOTALL)
    
    matches = pattern.findall(study_text)
    print(f"Extracted {len(matches)} questions.")
    
    # Print a few questions for preview
    for i, (q_num, q_body) in enumerate(matches[:5]):
        lines = q_body.strip().split('\n')
        q_text = lines[0]
        ans_text = "\n".join(lines[1:])
        print(f"--- Q{q_num} ---")
        print(f"Q: {q_text}")
        print(f"A: {ans_text[:100]}...")

if __name__ == '__main__':
    main()
