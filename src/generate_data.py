import json
import random
import os

def generate_mock_data():
    prs = []
    
    for i in range(1, 6):
        pr = {
            "pr_id": f"PR-{1000+i}",
            "title": f"Feature implementation {i}",
            "total_time_hours": random.randint(2, 20),
            "rounds": []
        }
        
        num_rounds = random.randint(2, 4)
        
        for r in range(1, num_rounds + 1):
            if r == 1:
                value_type = "high"
                comments = ["Found a security vulnerability", "Logic error in loop"]
                lines_changed = random.randint(10, 50)
            else:
                value_type = "low" 
                comments = ["Please rename variable x", "Missing semicolon", "LGTM"]
                lines_changed = random.randint(1, 5) 
            
            pr["rounds"].append({
                "round_number": r,
                "reviewer_comments": comments,
                "lines_of_code_changed": lines_changed,
                "time_spent_minutes": random.randint(10, 60),
                "value_assessment": value_type 
            })
            
        prs.append(pr)

    # --- FIXED PATH LOGIC ---
    # This finds the folder where this script lives, goes up one level, and finds 'data'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    
    # This creates the folder if it doesn't exist
    os.makedirs(data_dir, exist_ok=True) 
    
    file_path = os.path.join(data_dir, 'sample_reviews.json')

    with open(file_path, 'w') as f:
        json.dump(prs, f, indent=4)
    
    print(f"Data generated successfully at: {file_path}")

if __name__ == "__main__":
    generate_mock_data()