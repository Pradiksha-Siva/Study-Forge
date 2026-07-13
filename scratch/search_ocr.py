import json

def main():
    log_path = r"C:\Users\Pradiksha sivakumar\.gemini\antigravity\brain\fd989da7-3ad1-42a4-a549-b4ad03515e02\.system_generated\logs\transcript_full.jsonl"
    
    with open(log_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            content = data.get('content', '')
            tool_calls = data.get('tool_calls', [])
            
            # Convert tool calls to string for check
            tc_str = str(tool_calls)
            
            if "==Start of OCR for page 1==" in content:
                print(f"Line {idx} content contains page 1 OCR. Type: {data.get('type')}, Source: {data.get('source')}")
            if "==Start of OCR for page 8==" in content:
                print(f"Line {idx} content contains page 8 OCR.")
            if "==Start of PDF==" in content:
                print(f"Line {idx} content contains Start of PDF.")
            
            # Check inside tool calls/thinking
            thinking = data.get('thinking', '')
            if "==Start of OCR for page 1==" in thinking:
                print(f"Line {idx} thinking contains page 1 OCR.")

if __name__ == '__main__':
    main()
