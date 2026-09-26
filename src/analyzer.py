import json
import os

def analyze_reviews():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'sample_reviews.json')
    
    with open(data_file, 'r') as f:
        prs = json.load(f)

    low_value_rounds = []
    high_value_rounds = []
    total_wasted_minutes = 0
    
    for pr in prs:
        for round_data in pr['rounds']:
            # OPTION B LOGIC: Anything after round 2 is low value
            if round_data['round_number'] > 2:
                round_data['status'] = 'LOW_VALUE (Wasted Attention)'
                
                # --- THE FIX: Attach the PR ID to the round data ---
                round_data['pr_id'] = pr['pr_id'] 
                # ----------------------------------------------------
                
                low_value_rounds.append(round_data)
                total_wasted_minutes += round_data['time_spent_minutes']
            else:
                round_data['status'] = 'HIGH_VALUE'
                round_data['pr_id'] = pr['pr_id'] # Good practice to add it here too
                high_value_rounds.append(round_data)

    report = {
        "summary": {
            "total_prs_analyzed": len(prs),
            "total_high_value_rounds": len(high_value_rounds),
            "total_low_value_rounds": len(low_value_rounds),
            "total_time_wasted_minutes": total_wasted_minutes,
            "time_saved_hours": round(total_wasted_minutes / 60, 2)
        },
        "deleted_rounds": low_value_rounds
    }

    report_file = os.path.join(script_dir, '..', 'data', 'attention_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=4)

    print("="*50)
    print("🚀 HUMAN ATTENTION REPORT GENERATED 🚀")
    print("="*50)
    print(f"PRs Analyzed: {report['summary']['total_prs_analyzed']}")
    print(f"High Value Rounds: {report['summary']['total_high_value_rounds']}")
    print(f"Low Value Rounds (Deleted): {report['summary']['total_low_value_rounds']}")
    print(f"⏱️  Time Wasted on Low Value Rounds: {total_wasted_minutes} minutes")
    print(f"⏱️ Time Saved by Nilist: {report['summary']['time_saved_hours']} hours")
    print("="*50)
    print(f"Full report saved to: {report_file}")

if __name__ == "__main__":
    analyze_reviews()