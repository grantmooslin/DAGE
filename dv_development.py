"""
THIS IS A PROTOTYPE ONLY.
Uses excerpt data to test construction of the target variable.
Final scoring and labels should be rerun on the full cleaned dataset.
Creates group_ca_mean, one_on_one_ca_mean, and a binary preference class.
"""

import csv
from collections import Counter

# Likert scale mapping
LIKERT_MAPPING = {
    'Strongly disagree': 1,
    'Somewhat disagree': 2,
    'Neither agree nor disagree': 3,
    'Somewhat agree': 4,
    'Strongly agree': 5
}

# Define items and scoring direction
GROUP_ITEMS = {
    'direct': ['Q1', 'Q3', 'Q5'],
    'reverse': ['Q2', 'Q4', 'Q6']
}

ONE_ON_ONE_ITEMS = {
    'direct': ['Q13', 'Q15', 'Q18'],
    'reverse': ['Q14', 'Q16', 'Q17']
}

def reverse_score(score):
    """Reverse score: 6 - original_score"""
    return 6 - score

def map_likert(response):
    """Map text response to numeric score"""
    return LIKERT_MAPPING.get(response, None)

def load_and_process(filepath):
    """Load Qualtrics excerpt and process CA scores"""
    
    # Read CSV
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Remove metadata rows (rows 2 and 3, indices 1 and 2)
    # Keep row 1 (column names) and row 4+ (data)
    header = rows[0]
    data_rows = rows[3:]  # Skip rows 1, 2, 3 (indices 0, 1, 2)
    
    print("Loaded {} participant rows".format(len(data_rows)))
    
    # Process each participant
    results = []
    
    for row in data_rows:
        # Create dict for this row
        row_dict = dict(zip(header, row))
        
        # Score group items
        group_scores = []
        for item in GROUP_ITEMS['direct']:
            score = map_likert(row_dict[item])
            if score is not None:
                group_scores.append(score)
        
        for item in GROUP_ITEMS['reverse']:
            score = map_likert(row_dict[item])
            if score is not None:
                group_scores.append(reverse_score(score))
        
        # Score one-on-one items
        one_on_one_scores = []
        for item in ONE_ON_ONE_ITEMS['direct']:
            score = map_likert(row_dict[item])
            if score is not None:
                one_on_one_scores.append(score)
        
        for item in ONE_ON_ONE_ITEMS['reverse']:
            score = map_likert(row_dict[item])
            if score is not None:
                one_on_one_scores.append(reverse_score(score))
        
        # Calculate means (only if we have scores)
        group_ca_mean = sum(group_scores) / len(group_scores) if group_scores else None
        one_on_one_ca_mean = sum(one_on_one_scores) / len(one_on_one_scores) if one_on_one_scores else None
        
        # Derive class
        if group_ca_mean is None or one_on_one_ca_mean is None:
            derived_class = 'missing'
        elif group_ca_mean < one_on_one_ca_mean:
            derived_class = 'group'
        elif one_on_one_ca_mean < group_ca_mean:
            derived_class = 'one_on_one'
        else:
            derived_class = 'tie'
        
        results.append({
            'group_ca_mean': group_ca_mean,
            'one_on_one_ca_mean': one_on_one_ca_mean,
            'derived_class': derived_class
        })
    
    return results

if __name__ == "__main__":
    # Load and process
    filepath = '/Users/daseydang/Projects/DAGE/data_org/Excerpt For Testing Qualtrics Export.csv'
    results = load_and_process(filepath)
    
    # Print counts
    print("\nCLASS COUNTS:")
    classes = [r['derived_class'] for r in results]
    counts = Counter(classes)
    for class_name, count in counts.items():
        print("  {}: {}".format(class_name, count))
    
    # Print sample of results (first 10)
    print("\nSAMPLE RESULTS (first 10):")
    for i, r in enumerate(results[:10]):
        group_str = "{:.2f}".format(r['group_ca_mean']) if r['group_ca_mean'] is not None else "N/A"
        one_str = "{:.2f}".format(r['one_on_one_ca_mean']) if r['one_on_one_ca_mean'] is not None else "N/A"
        print("  Participant {}".format(i+1))
        print("    group_ca_mean: {}".format(group_str))
        print("    one_on_one_ca_mean: {}".format(one_str))
        print("    class: {}".format(r['derived_class']))
        print()
