import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
from Homepage import get_session_state, set_session_state
from streamlit_extras.switch_page_button import switch_page
from PIL import Image, ImageDraw, ImageOps
import io
import requests
from uuid import uuid4
import plotly.graph_objs as go
import plotly.express as px
import base64




# Connect to MongoDB
client = MongoClient("")
db = client.test
users = db.users
data = db.data

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .css-6qob1r {{
             background-image: url("https://images.unsplash.com/photo-1524169358666-79f22534bc6e?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=3540&q=80");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

def add_mbg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://images.unsplash.com/photo-1566410824233-a8011929225c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2340&q=80");
             background-attachment: fixed;
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_mbg_from_url()


def is_user_logged_in():
    return get_session_state().get("is_logged_in", False)

st.title("User Dashboard")

def add_logo():
    owner = " "
    repo = "test_testing"
    path = "test_logo.png"
    ref = "main"
    url = f"  "
    headers = {
        "Authorization": ""
    }
    response = requests.get(url, headers=headers)

    image_url = response.json()["download_url"]
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url({image_url});
                background-repeat: no-repeat;
                padding-top: 80px;
                background-position: 20px 20px;
                background-size: 50%;
            }}
            [data-testid="stSidebarNav"]::before {{
                content: "ODIN";
                font-family: "Apple Chancery", Helvetica, Arial, sans-serif;
                padding-left: 40px;
                padding-top: 20px;
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 90px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

if not is_user_logged_in():
    add_logo()
    st.error("You need to log in to access this page.")
    st.stop()


# Define today's date
today = datetime.now().strftime("%Y-%m-%d")

def get_user_state():
    # Get the session state for the current session ID
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    if st.session_state.session_id not in st.session_state:
        st.session_state[st.session_state.session_id] = {}
    return st.session_state[st.session_state.session_id]

# Add input field for subject name
subject_name = st.text_input("Enter subject name:")

# Add input field for teacher name
teacher_name = st.text_input("Enter your username:")

if st.button("Submit"):
    #fetch the data for the current month for the entered subject name and teacher name
    month_start = (datetime.now() - timedelta(days=datetime.now().day)).strftime("%Y-%m-%d")
    month_data = list(data.find({"date_verified": {"$gte": month_start}, "subject_name": subject_name, "teacher_name": teacher_name}))

    if len(month_data) > 0:
        # Create a DataFrame for the month's data
        df = pd.DataFrame(month_data)

        # Create a pie chart to show number of students present today
        present_today = df[df['date_verified'] == today]['Name'].nunique()
        absent_today = df - present_today

        chart_data = pd.DataFrame({
            'status': ['Present', 'Absent'],
            'students': [present_today, absent_today]
        })
        
        st.subheader('Attendance Statistics')
        st.write(chart_data.set_index('status'), width=200, height=200)
        st.plotly_chart(px.pie(chart_data, values='students', names='status'))

        # Create a bar chart to show number of students present each day this month
        attendance_by_day = df.groupby('date_verified')['Name'].nunique().reset_index()
        bar_chart = st.container()
        with bar_chart:
            st.subheader('Attendance This Month')
            st.info("Hover over the bars to see the number of students present on that day.")
            st.bar_chart(attendance_by_day.set_index('date_verified'))



    # Fetch the data for the current week for the entered subject name and teacher name
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
    week_data = list(data.find({"date_verified": {"$gte": week_start}, "subject_name": subject_name, "teacher_name": teacher_name}))

    if len(week_data) < 0:
        # Create a DataFrame for the week's data
        df = pd.DataFrame(week_data)

        # Create a pie chart to show number of students present today
        present_today = df[df['date_verified'] == today]['Name'].nunique()
        absent_today = df - present_today

        chart_data = pd.DataFrame({
            'status': ['Present', 'Absent'],
            'students': [present_today, absent_today]
        })
        
        import altair as alt

        # Create a bar chart to show number of students present each day this week
        attendance_by_day = df.groupby('date_verified')['Name'].nunique().reset_index()

        bar_chart = st.container()
        with bar_chart:
            st.subheader('Attendance This Week')
            chart = alt.Chart(attendance_by_day).mark_bar().encode(
                x=alt.X('Name:Q', title='Count'),
                y=alt.Y('date_verified:O', sort=alt.EnctestgSortField(field='date_verified', order='ascending'), title='Dates'),
                tooltip=['date_verified', 'Name']
            )
            st.altair_chart(chart, use_container_width=True)



        # Create a table to show student names and attendance count for the week
        attendance_table = st.container()
        with attendance_table:
            st.subheader('Attendance Table')
            st.info("Click on the 'Download Attendance file' button to download the attendance data as a csv file.")
            attendance_count = df.groupby('Name')['date_verified'].nunique().reset_index()
            attendance_count.columns = ['Name', 'Attendance Count']
            attendance_count = attendance_count[attendance_count['Name'] != 'Forgery'] # filter out "Forgery" name
            st.write(attendance_count)

            #add a download button to download the data as a csv file
            csv = attendance_count.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
            button_label = 'Download Attendance file'
            button_download_filename = 'attendance.csv'
            st.download_button(
                label=button_label,
                data=b64,
                file_name=button_download_filename,
                mime='text/csv',
            )
    else:
        st.warning("No data available for the entered subject name.")




# Redirect to Homepage button
go_to_homepage = st.button("Homepage")
if go_to_homepage:
    switch_page("Homepage")




# Main function
def main():
    add_logo() # Call the function to add logo to sidebar
    # st.title("Odin App")
    add_bg_from_url()
    add_mbg_from_url()

    session_state = get_session_state()


    if  session_state.get("is_logged_in", False):
        add_logo()
        # Create a sidebar container for logged in user info
        user_info_container = st.sidebar.container()
        with user_info_container:
            st.subheader(f"Logged in as {session_state['username']}")

            user = users.find_one({"username": get_session_state().get("username")})
            if user:
                # Show profile photo
                profile_photo = user.get("profile_photo")
                if profile_photo:
                    image = Image.open(io.BytesIO(profile_photo))
                    image = image.resize((100, 100))
                    image = image.convert("RGBA")

                    # Create circular mask
                    size = (100, 100)
                    mask = Image.new('L', size, 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0) + size, fill=255)

                    # Apply mask to image
                    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
                    output.putalpha(mask)

                    output_bytes = io.BytesIO()
                    output.save(output_bytes, format='PNG')
                    output_bytes.seek(0)

                    # Show profile photo
                    st.image(output_bytes, width=100)

        
        # Create a logout button container
        logout_container = st.sidebar.container()
        with logout_container:
            st.button("Logout", on_click=logout, key="logout_button")

def logout():
    set_session_state({"is_logged_in": False, "username": None})
    st._rerun()

if __name__ == "__main__":
    main()