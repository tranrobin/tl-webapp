import pandas as pd

df = pd.read_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/student_work_modeling/names_scores_for_robin.csv")
# Separate the baseline and other observations
baseline_df = df[df['direct_to_ts_obs'] == 'Baseline (first observation of the year)']
other_df = df[df['direct_to_ts_obs'] != 'Baseline (first observation of the year)']

# Pivot the other observations for easier lookup
pivot_df = other_df.pivot(index='teacher_select', columns='direct_to_ts_obs', values='overall_score')

# Create a new column for the appropriate observation to use for change calculation
pivot_df['final_score'] = pivot_df['End of year (last observation of the year)'].combine_first(
    pivot_df['Mid-year (middle of service, if applicable)']
).combine_first(
    pivot_df['Ongoing']
)

# Merge the baseline and final score data
result_df = baseline_df[['teacher_select', 'overall_score']].merge(
    pivot_df[['final_score']],
    left_on='teacher_select',
    right_index=True,
    how='left'
)

# Calculate the change from baseline to the appropriate final score
result_df['change'] = result_df['final_score'] - result_df['overall_score']
result_df['change'] = result_df['change'].fillna(result_df['overall_score'])
result_df["ipg_form_score"] = result_df["change"]
result_df = result_df[["teacher_select", "ipg_form_score"]]

# Show the result DataFrame
result_df.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/student_work_modeling/ipg_forms_score")
