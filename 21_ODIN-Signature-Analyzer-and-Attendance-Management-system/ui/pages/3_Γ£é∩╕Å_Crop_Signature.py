import streamlit as st
from pymongo import MongoClient
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import datetime
import os
import io
from Homepage import get_session_state, set_session_state
from streamlit_extras.switch_page_button import switch_page
import requests

# Connect to MongoDB
client = MongoClient("")
db = client.test
users = db.users

# st.title("Crop Signatures")

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
    response.raise_for_status()

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


def is_user_logged_in():
    return get_session_state().get("is_logged_in", False)


if not is_user_logged_in():
    add_logo()
    st.error("You need to log in to access this page.")
    st.stop()

def crop_signatures(image, coords, day):
    sign_folder = f"sign/{day}"
    if not os.path.exists(sign_folder):
        os.makedirs(sign_folder)

    cropped_signatures = []
    for i, box in enumerate(coords):
        x1, y1 = box[0]
        x2, y2 = box[1]
        signature = image[y1:y2, x1:x2]
        cropped_signatures.append(signature)
        st.write(f"Signatures for {day}:")
        st.image(signature, caption=f"Cropped signature {i+1} of {day}", use_column_width=True)

        # save the cropped signature to the sign_folder
        signature_path = os.path.join(sign_folder, f"signature_{i+1}.png")
        cv2.imwrite(signature_path, signature)

    return cropped_signatures



st.title("Signature Cropper")

st.sidebar.title("Signature Cropper")

COORDS = {
    "Monday": [[(731, 237), (1019, 344)], [(732, 347),  (1020, 455)], [(732, 459),  (1021, 567)], [(731, 568),  (1024, 677)], [(732, 680), (1019, 784)], [(729, 787), (1019, 893)],  [(731, 900), (1016, 1002)], [(732, 1009),  (1016, 1111)], [(730, 1125),  (1017, 1227)], [(726, 1236), (1018, 1335)]],
    "Tuesday": [[(1022, 238), (1307, 343)], [(1024, 346), (1306, 454)], [(1024, 458), (1306, 565)], [(1023, 569), (1306, 676)], [(1024, 680), (1308, 784)], [(1026, 788), (1305, 895)], [(1025, 899), (1305, 1002)], [(1025, 1008), (1305, 1116)], [(1025, 1122), (1305, 1228)], [(1025, 1235), (1306, 1337)]],
    "Wednesday": [[(1312, 236), (1601, 341)], [(1312, 343), (1598, 454)], [(1312, 457), (1602, 565)], [(1311, 565), (1597, 674)], [(1310, 678), (1601, 785)], [(1311, 786), (1599, 893)], [(1312, 898), (1598, 1002)], [(1313, 1005), (1601, 1118)], [(1313, 1121), (1603, 1230)], [(1314, 1232), (1602, 1336)]],
    "Thursday": [[(1607, 232), (1896, 338)], [(1604, 343), (1894, 453)], [(1603, 456), (1893, 561)], [(1601, 565), (1901, 686)], [(1601, 682), (1893, 784)], [(1603, 789), (1888, 893)], [(1604, 897), (1888, 999)], [(1604, 1006), (1888, 1113)], [(1607, 1124), (1892, 1226)], [(1608, 1230), (1896, 1334)]],
    "Friday": [[(1899, 230), (2184, 337)], [(1896, 344), (2178, 450)], [(1897, 456), (2180, 559)], [(1896, 564), (2180, 669)], [(1895, 679), (2176, 782)], [(1894, 784), (2177, 894)], [(1896, 899), (2183, 1002)], [(1895, 1007), (2181, 1115)], [(1894, 1120), (2185, 1227)], [(1896, 1230), (2186, 1335)]]
}


days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
selected_days = st.multiselect("Select the day(s) of the attendance sheet", days)
uploaded_file = st.file_uploader("Upload Attendance Sheet", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)
    st.image(image, caption="Original Image", use_column_width=True)

    for day in selected_days:
        coords = COORDS[day]
        cropped_signatures = crop_signatures(image, coords, day)

# Redirect to Homepage button
go_to_homepage = st.button("Homepage")
if go_to_homepage:
    switch_page("Homepage")

def main():
    # add_logo() # Call the function to add logo to sidebar
    # st.title("Odin App")

    session_state = get_session_state()
    add_logo()
    add_mbg_from_url()
    add_bg_from_url()

    if  session_state.get("is_logged_in", False):
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