import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import OneHotEncoder
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import base64
import streamlit as st

# Load your trained model and encoder
model = joblib.load('rf_weights_guskey.pkl')
encoder = joblib.load('encoder.pkl')
feature_names = joblib.load('feature_names.pkl')
data = pd.read_csv("student_work_prediction.csv")

data["content_area"] = data["content_area"].replace("K-2 Early Literacy (Foundational Skills)", "K-2 Early Literacy")

# Rename columns as needed
data['coach_end_feed_4'] = data['coach_end_feed_4']
data['coach_end_feed_3'] = data['coach_end_feed_15']
data['coach_end_feed_2'] = data['coach_end_feed_16']
data['coach_end_feed_5'] = data['coach_end_feed_10']
columns_to_drop = ['coach_end_feed_15', 'coach_end_feed_16', 'coach_end_feed_10']
data = data.drop(columns=columns_to_drop)
data = data.drop(data.columns[0], axis=1)

# Set page title and layout
st.set_page_config(page_title="Integrating Multi-Survey Data", layout="wide")

def show_introduction():
    image_path = "tllogo.png"
    st.image(image_path, width=300)
    
    st.title("Integrating Multi-Survey Data for Better Student Performance Predictions and Teacher Training Evaluation")
    st.subheader("Research Question:")
    st.markdown("""How can the integration of various teacher and student survey responses provide a more comprehensive prediction of student performance and offer insights into teacher effectiveness?
    """)
    st.subheader("Explanation:")
    st.markdown("""
To achieve a comprehensive prediction of student performance, we focus on the Student Work's score, which reflects the overall quality of a teacher's students' work. 
This project aims to enhance this prediction by incorporating additional data sources and responses from various surveys. 

Each of these surveys is conducted separately and uses different formats for identifying participants, necessitating an extensive process of matching IDs across surveys to create a unified and comprehensive dataset for modeling. 

By integrating these diverse data sources, the goals are to develop a more comprehensive model for predicting student performance by combining multiple data points rather than relying solely on Student Work scores and identify potential strong correlations between various factors (e.g., teacher's responses in Participant Feedback, Classroom Observation scores) and the Student Work scores.
""")
    st.subheader("Navigation:")
    st.markdown("""
    - **Data Processing Pipeline:** Explanation of the data processing steps.
    - **Data Visualization:** Visual representations of the data.
    - **Model Prediction:** Predict student performance based on survey responses.
    """)

# Define the pages
def show_workflow():
    st.header("Data Processing Pipeline")
    image_path = "tlbig.jpg"
    
    def get_image_base64(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string

    def display_image(image_path):
        img_base64 = get_image_base64(image_path)
        img_html = f'<img src="data:image/png;base64,{img_base64}" style="width:100%;height:auto;">'
        st.markdown(img_html, unsafe_allow_html=True)

    display_image(image_path)
    st.markdown("""
    ### Data Storage and Initial Processing:
    - **Source:** Different school year folders on S3 (historical-data-raw-tl).
    - **Process:** Merge/process/clean them into historical datasets by merging columns/variables within a survey but throughout all school years.
    - **Destination:** S3 (historical-data-clean-tl).

    ### New Data Integration:
    - **Source:** Qualtrics for Educator Survey.
    - **Process:** Pull responses from Qualtrics, process them, and add to the existing historical dataset.
    - **Tool:** Airflow.
    - **Destination:** S3 (historical-data-clean-tl).

    ### ID Matching across Surveys:
    - **Input:** Historical datasets (Educator Survey, Participant Feedback, Student Work, IPG Form, Knowledge Assessment).
    - **Process:** Match IDs across all historical survey datasets to generate metadata about respondents.
    - **Method:** Generate potential email variants using teachers' names and site, then match to real emails using fuzzy string matching.
    - **Output:** Comprehensive teacher profile (demographics, different info from multi-survey).

    ### Data Visualization:
    - **Process:** Process and visualize surveys data, focusing on Student Work's grade.

    ### Machine Learning Model:
    - **Input:** Processed teacher data.
    - **Process:** Fit the model to predict Student Work's grade using variables from Participant Feedback and IPG forms.
    - **Output:** Model predictions and feature importances.

    ### Deployment:
    - **Tool:** Streamlit webapp.
    - **Process:** Deploy the model to Streamlit for predictions and feature importances.
    """)

def show_visualizations():
    st.header("Data Visualization")
    
    # Compute metrics
    promoter_percentage = data['nps_all'].value_counts(normalize=True).get('Promoter', 0) * 100
    average_ipg_form_score = data['ipg_form_score'].mean()
    average_coach_end_feed_1 = data[['coach_end_feed_1', 'coach_end_feed_2', 'coach_end_feed_3', 'coach_end_feed_4', 'coach_end_feed_5']].mean().mean()
    mode_grade_2_percentage = data['Mode Grade'].value_counts(normalize=True).get(2, 0) * 100

    # Display the metrics as a dashboard
    st.header('General Metrics')
    col1, space1, col2, space2, col3, space3, col4 = st.columns([1, 0.1, 1, 0.1, 1, 0.1, 1])
    with col1:
        st.metric(label="Promoter Percentage", value=f"{promoter_percentage:.2f}%", delta="-5.71% from last week")
        st.caption('Percentage of Promoter in NPS ratings.')
    with col2:
        st.metric(label="Average IPG Form Score", value=f"{average_ipg_form_score:.2f}", delta="-0.2% from last week")
        st.caption('Average score from Classroom Observation.')
    with col3:
        st.metric(label="Average Coach End Feedback", value=f"{average_coach_end_feed_1:.2f} / 5", delta="+0.91% from last week")
        st.caption('Average ratings from participants on coach.')
    with col4:
        st.metric(label="Mode Grade 2 Percentage", value=f"{mode_grade_2_percentage:.2f}%", delta="+3.45% from last week")
        st.caption('Percentage of Teachers with Student Work graded 2.')
    st.markdown("&nbsp;")

    # Display the reviews
    if st.checkbox('Show all reviews'):
        st.write(data)
    else:
        st.write("Top 5 data points:")
        st.write(data.head(5))

    st.markdown("&nbsp;")

    # Chart Breakdown
    st.header('Chart Breakdown')

    # Sidebar filters
    palette = ["#EF5A6F", "#536493", "#FFF1DB"]

# Sidebar filters
    site_state_filter = st.sidebar.multiselect("Select Site State", options=data['site_state'].unique(), default=data['site_state'].unique())
    race_filter = st.sidebar.multiselect("Select Race", options=data['race'].unique(), default=data['race'].unique())
    gender_filter = st.sidebar.multiselect("Select Gender", options=data['gender'].unique(), default=data['gender'].unique())

    # Apply filters to the data
    filtered_data = data[(data['site_state'].isin(site_state_filter)) & 
                        (data['race'].isin(race_filter)) & 
                        (data['gender'].isin(gender_filter))]

    # Chart Breakdown

    # Gender Pie Chart + Mode Grade Distribution by Gender
    st.subheader('Gender Distribution and Mode Grade Distribution by Gender')
# Gender Pie Chart + Mode Grade Distribution by Gender
    col1, space, col2 = st.columns([0.7, 0.1, 1])
    with col1:
        fig1 = px.pie(filtered_data, names='gender', title='Gender Distribution', color_discrete_sequence=palette)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.histogram(filtered_data, x='gender', color='Mode Grade', barmode='group', title='Mode Grade Distribution by Gender', color_discrete_sequence=palette)
        st.plotly_chart(fig2, use_container_width=True)
    st.subheader('Content Area Distribution and Mode Grade Distribution by Content Area')
    # Content Area Pie Chart + Mode Grade Distribution by Content Area
    col1, space, col2 = st.columns([0.7, 0.1, 1])
    with col1:
        fig3 = px.pie(filtered_data, names='content_area', title='Content Area Distribution', color_discrete_sequence=palette)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        fig4 = px.histogram(filtered_data, x='content_area', color='Mode Grade', barmode='group', title='Mode Grade Distribution by Content Area', color_discrete_sequence=palette)
        st.plotly_chart(fig4, use_container_width=True)

    # Stacked Barchart of Mode Grade by Site State + Stacked Barchart of Mode Grade by Race
    st.subheader('States Distribution and Mode Grade Distribution by States')
    col1, space, col2 = st.columns([0.5, 0.1, 1])
    with col1:
        fig6 = px.treemap(filtered_data, path=['site_state'], title='State Distribution', color_discrete_sequence=palette)
        st.plotly_chart(fig6, use_container_width=True)
    with col2:
        fig5 = px.histogram(filtered_data, y='site_state', color='Mode Grade', title='Mode Grade Distribution by Site State', barmode='stack', orientation='h', color_discrete_sequence=palette)
        st.plotly_chart(fig5, use_container_width=True)
    st.subheader('Mode Grade Distribution by Race')
    fig5 = px.histogram(filtered_data, x='race', color='Mode Grade', barmode='group', title='Mode Grade Distribution by Race', color_discrete_sequence=palette)
    fig5.update_layout(height=500) 
    st.plotly_chart(fig5, height = 500, use_container_width=True)

    # Violin Plot of IPG Form Score and Mode Grade
    st.subheader('Classroom Observation Score and Mode Grade Distribution')
    fig7 = px.violin(filtered_data, x='Mode Grade', y='ipg_form_score', title='IPG Form Score by Mode Grade', color='Mode Grade', box=True, points='all', color_discrete_sequence=palette)
    fig7.update_layout(height=500)  # Set the height of the figure
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader('NPS Score Distribution and Mode Grade Distribution by NPS')
    col1, space, col2 = st.columns([0.7, 0.1, 1])
    with col1:
        fig1 = px.pie(filtered_data, names='nps_all', title='NPS Distribution', color_discrete_sequence=palette)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.histogram(filtered_data, x='nps_all', color='Mode Grade', barmode='group', title='Mode Grade Distribution by NPS', color_discrete_sequence=palette)
        st.plotly_chart(fig2, use_container_width=True)

    # melted_data = pd.melt(data, id_vars=['Mode Grade'], value_vars=['coach_end_feed_1', 'coach_end_feed_2', 'coach_end_feed_3', 'coach_end_feed_4', 'coach_end_feed_5'],
    #                   var_name='Coach End Feedback', value_name='Feedback Score')

    # # Create a grouped bar chart
    # fig = px.histogram(melted_data, x='Feedback Score', color='Mode Grade', facet_col='Coach End Feedback', barmode='group',
    #                title='Mode Grade Distribution by Coach End Feedback Scores', color_discrete_sequence=pal)

    # # Display the chart in Streamlit
    # st.subheader('Mode Grade Distribution by Coach End Feedback Scores')
    # st.plotly_chart(fig, use_container_width=True)
def show_predictions():
    st.header("Student Work Model Prediction")
    st.markdown("""
    Our model utilizes the following data sources:
    - **Teachers' Demographics:** Information such as state, gender, and race.
    - **Teachers' Content Area:** Math, ELA, or K-2 Early Literacy (Foundational Skills).
    - **Participant Feedback:** Teachers' responses about the training and coaches.
    - **Classroom Observation Scores:** Evaluations rated by Teaching Lab staff - the percentage of positive indicators of any given respondent.
    - **NPS Ratings:** Teachers' Net Promoter Score (NPS) ratings, indicating their likelihood to recommend the training to others.

    """)

    # Create columns for sliders
    col1, col2 = st.columns(2)

    with col1:
        coach_end_feed_1 = st.slider('I looked forward to attending this PL.', min_value=1, max_value=5, value=3)
        coach_end_feed_15 = st.slider('I was fully present/”minds-on” during these PL sessions.', min_value=1, max_value=5, value=3)
        coach_end_feed_10 = st.slider('The activities were well-designed to help me meet the learning targets.', min_value=1, max_value=5, value=3)

    with col2:
        coach_end_feed_4 = st.slider('I am satisfied with how the sessions were facilitated.', min_value=1, max_value=5, value=3)
        coach_end_feed_16 = st.slider('This PL was a good use of my time. ', min_value=1, max_value=5, value=3)
        ipg_form_score = st.slider("Classroom Observation Score", min_value=0, max_value=100, value=50)

    # Input fields for categorical variables
    site_state = st.selectbox('Site State', ['LA', 'MA', 'NY', 'OH', 'TN'])
    content_area = st.selectbox('Content Area', ['Math', 'ELA', 'K-2 Early Literacy (Foundational Skills)'])
    nps_all = st.selectbox('NPS', ['Detractor', 'Passive', 'Promoter'])
    gender = st.selectbox('Gender', ['Female', 'Male', 'Prefer not to say'])
    race = st.selectbox('Race', ['Asian', 'Black', 'Hispanic', 'More than one race', 'Prefer not to say', 'Unknown', 'White'])

    # Create a DataFrame for the input
    input_data = pd.DataFrame({
        'nps_all': [nps_all],
        'gender': [gender],
        'race': [race],
        'ipg_form_score': [ipg_form_score],
        'site_state': [site_state],
        'content_area': [content_area],
        'coach_end_feed_1': [coach_end_feed_1],
        'coach_end_feed_4': [coach_end_feed_4],
        'coach_end_feed_15': [coach_end_feed_15],
        'coach_end_feed_16': [coach_end_feed_16],
        'coach_end_feed_10': [coach_end_feed_10]
    })

    encoded_input = encoder.transform(input_data[['nps_all', 'race', 'site_state', 'gender', 'content_area']])
    encoded_input_df = pd.DataFrame(encoded_input, columns=encoder.get_feature_names_out(['nps_all', 'race', 'site_state', 'gender', 'content_area']))

    # Combine encoded categorical features with continuous features
    input_data = input_data.drop(columns=['nps_all', 'gender', 'race', 'site_state', 'content_area'])
    input_data = pd.concat([input_data, encoded_input_df], axis=1)

    # Reorder the columns to match the expected order
    input_data = input_data.reindex(columns=feature_names)

    # Predict and display the result
    if st.button('Predict'):
        prediction = model.predict(input_data)
        st.write(f'Predicted Mode Grade: {prediction[0]}')
    
    image_path_importance = "importance.png"
    st.image(image_path_importance, use_column_width=True)

# Sidebar for navigation
page = st.sidebar.selectbox("Choose a page", ["Introduction", "Data Processing Pipeline", "Data Visualization", "Model Prediction"])

# Show the selected page
if page == "Introduction":
    show_introduction()
elif page == "Data Processing Pipeline":
    show_workflow()
elif page == "Data Visualization":
    show_visualizations()
else:
    show_predictions()
