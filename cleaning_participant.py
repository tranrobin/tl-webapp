import pandas as pd
from collections import Counter
import re

filtered_user_matching = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/id_matching/survey_user_matching.csv')
educator_survey = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/educator_survey.csv')
participant_feedback = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/historical_merging/output/merged_participant_feedback.csv')
student_work_without_22_23 = pd.read_csv('/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/historical_merging/output/student_work.csv')
student_work = pd.read_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/historical_merging/output/student_work.csv")
ipg_forms = pd.read_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/data_processing/historical_merging/output/merged_ipg_forms.csv")
participant_feedback = participant_feedback[['matched_id', 'initials', 'site', 'coach_end_feed_1', 'coach_end_feed_4', 'coach_end_feed_15', "coach_end_feed_16", "coach_end_feed_10", "coach_ongoing_feed_1","coach_ongoing_feed_2","coach_ongoing_feed_3","coach_ongoing_feed_4","coach_ongoing_feed_5", "fac_feedback_1", "fac_feedback_2", "fac_feedback_3", "fac_feedback_4", "fac_feedback_5", "nps_all", "gender", "race_1", "race_2", "race_3", "race_4", "race_5", "race_6", "race_7"]]
ipg_forms_score = pd.read_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/student_work_modeling/ipg_forms_score.csv")
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

student_work["id"] = student_work["email"].combine_first(student_work["Name"])
# Group by Teacher email and calculate the mode of grades
teacher_grades = student_work.groupby('id')['Normalized Grades'].apply(lambda x: calculate_mode(sum(x, []))).reset_index()
teacher_grades.columns = ['id', 'Mode Grade']
teacher_grades['Mode Grade'] = teacher_grades['Mode Grade'].fillna(0).apply(lambda x: int(float(x)))

student_work_unique = student_work.drop_duplicates(subset=['id'])

#student_work_unique.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_unique_v1.csv")

student_work_with_mode = student_work_unique.merge(teacher_grades, on='id', how='left')
student_work_with_mode.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_mode_v1.csv")

filtered_user_matching['email'] = filtered_user_matching['email/initials']
filtered_user_matching['name'] =  filtered_user_matching['name']

filtered_user_matching = filtered_user_matching.dropna(subset="email")
filtered_user_matching = filtered_user_matching.dropna(subset="name")
filtered_user_matching['email'] = filtered_user_matching['email'].str.lower()
filtered_user_matching['name'] = filtered_user_matching['name'].str.lower()

print(participant_feedback.columns)

participant_feedback["email"] = participant_feedback["matched_id"]
participant_feedback['email'] = participant_feedback['email'].str.lower()
participant_feedback = participant_feedback.dropna(subset="email")
participant_feedback = participant_feedback.drop_duplicates(subset=["email"])

#participant_feedback.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/participant_feedback_coalesce.csv")

#filtered_user_matching.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/filtered_combined_first.csv")
merged_df_user_match_edusurvey = filtered_user_matching.merge(participant_feedback, how = 'inner', on = 'email')
#merged_df_user_match_edusurvey.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/filtered_combined_first_merged_edu_survey_v1.csv")
merged_df_user_match_edusurvey['email']=merged_df_user_match_edusurvey['email'].drop_duplicates()
merged_df_user_match_edusurvey = merged_df_user_match_edusurvey.dropna(subset = 'email')
#merged_df_user_match_edusurvey.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/merged_df_user_match_edusurvey_v1.csv")

merged_df_user_match_edusurvey['email'] = merged_df_user_match_edusurvey['email'].str.lower()
#merged_df_user_match_edusurvey.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/merged_df_user_match_edusurvey_upper.csv")


student_work_with_mode['id'] = student_work_with_mode['id'].str.lower()
student_work_with_mode.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/student_work_with_mode_v1.csv")

# merged_df_user_match_edusurvey_student_work = merged_df_user_match_edusurvey.merge(student_work_with_mode, how = 'inner', left_on = 'email', right_on = 'Teacher Name')
# merged_df_user_match_edusurvey_student_work.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/final_merged_df_before.csv")

merged_df_user_match_edusurvey_student_work_teacher_email = merged_df_user_match_edusurvey.merge(student_work_with_mode, how = 'inner', left_on = 'email', right_on = 'id')
merged_df_user_match_edusurvey_student_work_teacher_name = merged_df_user_match_edusurvey.merge(student_work_with_mode, how = 'inner', left_on = 'name', right_on = 'id')
merged_df_user_match_edusurvey_student_work_teacher_email_name = pd.concat([merged_df_user_match_edusurvey_student_work_teacher_email, merged_df_user_match_edusurvey_student_work_teacher_name])


ipg_forms['teacher'] = ipg_forms['teacher'].str.lower()

merged_df_user_match_edusurvey_student_work_teacher_email_name_ipg = merged_df_user_match_edusurvey_student_work_teacher_email_name.merge(ipg_forms, how = "left", left_on = 'name', right_on = 'teacher')

merged_df_user_match_edusurvey_student_work_teacher_email_name_ipg.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/db/output/final_merged_df_part_student_v6.csv")

merged_df_user_match_edusurvey_student_work_teacher_email_name_ipg_score = merged_df_user_match_edusurvey_student_work_teacher_email_name_ipg.merge(ipg_forms_score, how = "left", left_on = "name", right_on = "teacher_select")
merged_df_user_match_edusurvey_student_work_teacher_email_name_ipg_score = merged_df_user_match_edusurvey_student_work_teacher_email_name_ipg_score.drop_duplicates(subset="name")
merged_df_user_match_edusurvey_student_work_teacher_email_name_ipg_score.to_csv("/Users/robintran/Desktop/TL/Python_Guskey_Analysis/analysis/student_work_modeling/final_df.csv")