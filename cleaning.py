import pandas as pd
from collections import Counter
import re

# Load the data
user_matching = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/id_matching/id_matching_ver2/data_post_edusurvey.csv')
educator_survey = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/educator_survey.csv')
participant_feedback = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/participant_feedback.csv')
student_work_without_22_23 = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/historical_merging/output/student_work_v2.csv')
student_work = pd.read_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/historical_merging/output/student_work_v2_22_23.csv")

# student_work = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_fix.csv')

# Filter user_matching for rows where "Student Work", "Participant Survey", and "Educator Survey" are all "Yes"
filtered_user_matching = user_matching

# Coalesce Teacher Name and Teacher Email in student_work
student_work['Teacher Name'] = student_work['Teacher Name'].combine_first(student_work['Teacher Email'])

# student_work['Teacher Name'] = student_work['Teacher Name'].combine_first(student_work['Teacher Initials'])

student_work['Teacher Name'] = student_work['Teacher Name'].str[:-4]
student_work['Teacher Name'] = student_work['Teacher Name'].str.upper()
student_work['Teacher Name'] = student_work['Teacher Name'].drop_duplicates()
student_work.to_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_v1.csv')

educator_survey_v1 = educator_survey[['email', 'site', 'content_area', 'mindsets_ts_1_1', 'mindsets_ts_1_2', 'mindsets_ts_1_4', 'mindsets_ts_1_5', 'mindsets_ts_1_6', 'mindsets_ts_1_13', 'mindsets_ts_1_16']]




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


teacher_grades_initials = student_work.groupby('Teacher Initials')['Normalized Grades'].apply(lambda x: calculate_mode(sum(x, []))).reset_index()
teacher_grades_initials.columns = ['Teacher Initials', 'Mode Grade']

# Ensure the grade format is correct (convert to integer if needed)
teacher_grades['Mode Grade'] = teacher_grades['Mode Grade'].fillna(0).apply(lambda x: int(float(x)))


teacher_grades_initials['Mode Grade'] = teacher_grades_initials['Mode Grade'].fillna(0).apply(lambda x: int(float(x)))


# Merge the mode grade back to the unique teacher entries
student_work_unique = student_work.drop_duplicates(subset=['Teacher Name', 'Teacher Initials'])
student_work_unique.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_unique_v1.csv")


student_work_with_mode_wo_initials = student_work_unique.merge(teacher_grades, on='Teacher Name', how='left')
student_work_with_mode = student_work_with_mode_wo_initials.merge(teacher_grades_initials, on = 'Teacher Initials', how = 'left')


student_work_with_mode.to_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_v5.csv')

# def normalize_grades(grades):
#     normalized = []
#     for grade in grades.split(','):
#         grade = grade.strip().replace('.0', '')
#         if grade.isdigit():
#             normalized.append(int(grade))
#     return normalized
    
# student_work['Normalized Grades'] = student_work['Submitted Grade/s'].apply(normalize_grades)
# # Normalize and extract grades

# student_work['Normalized Grades'] = student_work['Submitted Grade/s'].apply(normalize_grades)
# student_work.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_normalized_grades.csv")

# # Calculate the mode for each teacher
# def calculate_mode(grades):
#     if not grades:
#         return None
#     counter = Counter(grades)
#     mode = counter.most_common(1)
#     return mode


# teacher_grades = student_work.groupby('Teacher Name')['Normalized Grades'].apply(lambda x: calculate_mode(sum(x, []))).reset_index()
# teacher_grades.columns = ['Teacher Name', 'Mode Grade']

# student_work = student_work.merge(teacher_grades, on='Teacher Name', how='left')
# student_work.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_normalized_grades_teacher_grades.csv")


filtered_user_matching['email'] = filtered_user_matching['email/initials']

filtered_user_matching = filtered_user_matching.dropna(subset="email")


filtered_user_matching.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/filtered_combined_first.csv")
merged_df_user_match_edusurvey = filtered_user_matching.merge(educator_survey_v1, how = 'inner', on = 'email')
merged_df_user_match_edusurvey.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/filtered_combined_first_merged_edu_survey_v1.csv")
merged_df_user_match_edusurvey['email']=merged_df_user_match_edusurvey['email'].drop_duplicates()
merged_df_user_match_edusurvey = merged_df_user_match_edusurvey.dropna(subset = 'email')
merged_df_user_match_edusurvey.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/merged_df_user_match_edusurvey_v1.csv")

merged_df_user_match_edusurvey['email'] = merged_df_user_match_edusurvey['email'].str.upper()
merged_df_user_match_edusurvey.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/merged_df_user_match_edusurvey_upper.csv")


student_work_with_mode['Teacher Name'] = student_work_with_mode['Teacher Name'].str.upper()
student_work_with_mode['Teacher Email'] = student_work_with_mode['Teacher Email'].str.upper()
student_work_with_mode.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_with_mode_v1.csv")


merged_df_user_match_edusurvey_student_work = merged_df_user_match_edusurvey.merge(student_work_with_mode, how = 'inner', left_on = 'email', right_on = 'Teacher Name')
merged_df_user_match_edusurvey_student_work.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/final_merged_df_before.csv")

merged_df_user_match_edusurvey_student_work_teacher_email = merged_df_user_match_edusurvey.merge(student_work_with_mode, how = 'inner', left_on = 'email', right_on = 'Teacher Email')
merged_df_user_match_edusurvey_student_work_teacher_email.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/final_merged_df_teacher_email.csv")


merged_df_user_match_edusurvey_student_work_teacher_email_initials = merged_df_user_match_edusurvey.merge(student_work_with_mode, how = 'inner', left_on = 'email', right_on = 'Teacher Initials')
merged_df_user_match_edusurvey_student_work_teacher_email_initials.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/final_merged_df_teacher_email_initials.csv")



merged_df_user_match_edusurvey_student_work_final_p1 = pd.concat([merged_df_user_match_edusurvey_student_work,  merged_df_user_match_edusurvey_student_work_teacher_email, merged_df_user_match_edusurvey_student_work_teacher_email_initials], ignore_index=True)
merged_df_user_match_edusurvey_student_work_final_p1['Mode Grade_x'] = merged_df_user_match_edusurvey_student_work_final_p1['Mode Grade_x'].combine_first(merged_df_user_match_edusurvey_student_work_final_p1['Mode Grade_y'])
merged_df_user_match_edusurvey_student_work_final_p1.rename(columns={'Mode Grade_x': 'Mode Grade'}, inplace=True)

merged_df_user_match_edusurvey_student_work_final_p1.drop(columns=['Mode Grade_y'], inplace=True)


merged_df_user_match_edusurvey_student_work_final_p1.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/student_work_modeling/guskey_framework_v6.csv")


# merged_df = filtered_user_matching.merge(student_work, how='left', left_on='Initials', right_on='Teacher Name')
# merged_df = filtered_user_matching.merge(educator_survey, how='inner', on='email')

# filtered_user_matching = filtered_user_matching[['Name', 'email', 'Initials']]
# student_work = student_work[['Teacher Name', 'Teacher Email']]
# educator_survey = educator_survey[['email', 'site']]
# participant_feedback = participant_feedback[['email', 'content_area', 'initials']]

# participant_feedback['email'] = participant_feedback['email'].combine_first(participant_feedback['initials'])
# filtered_user_matching = filtered_user_matching.dropna(subset="email")

# # Select necessary columns


# # Perform left join with student_work where Teacher Email is not NA
# filtered_user_matching= filtered_user_matching.merge(educator_survey, how='left', on='email')

# filtered_user_matching = filtered_user_matching.merge(participant_feedback, how = 'left', on="email")

# merged_df = filtered_user_matching.merge(student_work_with_mode, how='left', left_on='Name', right_on='Teacher Name')
# filtered_user_matching = filtered_user_matching.drop_duplicates()
# Perform left join with educator_survey on email
# merged_df.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/merged.csv")