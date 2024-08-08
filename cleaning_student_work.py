import pandas as pd
from collections import Counter

# Load the data
user_matching = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/user_matching.csv')
educator_survey = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/educator_survey.csv')
participant_feedback = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/participant_feedback.csv')
student_work = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/historical_merging/output/student_work_v2.csv')

# Filter user_matching for rows where "Student Work", "Participant Survey", and "Educator Survey" are all "Yes"
filtered_user_matching = user_matching[(user_matching["Student Work"] == "Yes") & 
                                       (user_matching["Participant Feedback"] == "Yes") & 
                                       (user_matching["Educator Survey"] == "Yes")]

# Coalesce Teacher Name and Teacher Email
student_work['Teacher Name'] = student_work['Teacher Name'].combine_first(student_work['Teacher Email'])

# Normalize and extract grades
def normalize_grades(grades):
    if pd.isna(grades):
        return []
    normalized = []
    for grade in grades.split(','):
        grade = grade.strip().replace('.0', '')
        if grade.isdigit():
            normalized.append(int(grade))
    return normalized

student_work['Normalized Grades'] = student_work['Submitted Grade/s'].apply(normalize_grades)

# Calculate the mode for each teacher
def calculate_mode(grades):
    if not grades:
        return None
    counter = Counter(grades)
    mode, _ = counter.most_common(1)[0]
    return mode

# Group by Teacher Name and calculate the mode of grades
teacher_grades = student_work.groupby('Teacher Name')['Normalized Grades'].apply(lambda x: calculate_mode(sum(x, []))).reset_index()
teacher_grades.columns = ['Teacher Name', 'Mode Grade']

# Ensure the grade format is correct (convert to integer if needed)
teacher_grades['Mode Grade'] = teacher_grades['Mode Grade'].fillna(0).apply(lambda x: int(float(x)))

# Merge the mode grade back to the unique teacher entries
student_work_unique = student_work.drop_duplicates(subset=['Teacher Name'])
student_work_with_mode = student_work_unique.merge(teacher_grades, on='Teacher Name', how='left')

student_work_with_mode.to_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_v4.csv')
