import json
import os


# ── CORE ANALYSIS FUNCTION ─────────────────────────────────────────────────────
def analyze_data(prs_list: list) -> dict:
    """
    Analyse a list of PR dictionaries and return a report dictionary.

    Args:
        prs_list: A list of PR objects, each with a 'pr_id' key and a
                  'rounds' list.  This is the direct result of json.load()
                  on a sample_reviews-style JSON file — no file I/O happens
                  inside this function.

    Returns:
        A dict with two keys:
          'summary'        – aggregated counts and time figures
          'deleted_rounds' – list of individual low-value round objects
    """
    low_value_rounds  = []
    high_value_rounds = []
    total_wasted_minutes = 0

    for pr in prs_list:
        for round_data in pr['rounds']:
            # Deep-copy the round so we don't mutate the caller's data
            rd = dict(round_data)
            rd['pr_id'] = pr['pr_id']

            # Option B logic: anything after round 2 is low-value
            if rd['round_number'] > 2:
                rd['status'] = 'LOW_VALUE (Wasted Attention)'
                low_value_rounds.append(rd)
                total_wasted_minutes += rd['time_spent_minutes']
            else:
                rd['status'] = 'HIGH_VALUE'
                high_value_rounds.append(rd)

    report = {
        "summary": {
            "total_prs_analyzed":        len(prs_list),
            "total_high_value_rounds":   len(high_value_rounds),
            "total_low_value_rounds":    len(low_value_rounds),
            "total_time_wasted_minutes": total_wasted_minutes,
            "time_saved_hours":          round(total_wasted_minutes / 60, 2),
        },
        "deleted_rounds": low_value_rounds,
    }

    return report


# ── CLI ENTRY POINT ────────────────────────────────────────────────────────────
def analyze_reviews():
    """Read sample_reviews.json from the default location and write the report."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file  = os.path.join(script_dir, '..', 'data', 'sample_reviews.json')

    with open(data_file, 'r') as f:
        prs = json.load(f)

    report = analyze_data(prs)

    report_file = os.path.join(script_dir, '..', 'data', 'attention_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=4)

    print("=" * 50)
    print("🚀 HUMAN ATTENTION REPORT GENERATED 🚀")
    print("=" * 50)
    print(f"PRs Analyzed:                  {report['summary']['total_prs_analyzed']}")
    print(f"High-Value Rounds:             {report['summary']['total_high_value_rounds']}")
    print(f"Low-Value Rounds (Deleted):    {report['summary']['total_low_value_rounds']}")
    print(f"⏱  Time Wasted:               {report['summary']['total_time_wasted_minutes']} minutes")
    print(f"⏱  Time Saved by Nilist:      {report['summary']['time_saved_hours']} hours")
    print("=" * 50)
    print(f"Full report saved to: {report_file}")


if __name__ == "__main__":
    analyze_reviews()
