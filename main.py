###################################
#     Importing dependencies      #
###################################

import streamlit as st
import mediapipe as mp 
import cv2 
import csv
import os
import numpy as np
import time

mp_drawing = mp.solutions.drawing_utils 
mp_holistic = mp.solutions.holistic 


###################################
#       Necessary Functions       #
###################################


def mediapipe_only(image:str, class_name:str):
  try:
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        # Make Detections
        results = holistic.process(image)
        # Recolor image back to BGR for rendering
        image.flags.writeable = True   
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # 1. Draw face landmarks
        mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION, 
                                 mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                                 mp_drawing.DrawingSpec(color=(80,256,121), thickness=1, circle_radius=1)
                                 )
        
            # 2. Right hand
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                 mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                 mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                 )

            # 3. Left Hand
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                 mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
                                 mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                 )

            # 4. Pose Detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
                                 mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
                                 mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                 )
            # Export coordinates
        try:
                # Extract Pose landmarks
            pose = results.pose_landmarks.landmark
            pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())
            
                # Extract Face landmarks
            face = results.face_landmarks.landmark
            face_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in face]).flatten())
            
                # Concate rows
            row = pose_row+face_row
            
                # Append class name 
            row.insert(0, class_name)
            if len(row)>1:
            # Export to CSV
                with open('coords.csv', mode='a', newline='') as f:
                    csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow(row) 
            else:
                st.write("Didn't write blank row to csv")
        except:
            st.error(str="Failed to write CSV",icon="🚨")
    return True
  except:
    return False
         
       
###################################
#   STARTING THE WEBPAGE CODE     #
###################################
st.title("DATASET GENERATOR")
class_name = st.selectbox(
        "Which gesture/emotion do you want to show?",
        ("Happy", "Sad", "Confused","Fear")
    )

upload_tab, click_tab = st.tabs(["Upload", "Click a picture"])

with upload_tab:
    value_progress_bar=0
    my_bar = st.progress(value_progress_bar)
    uploaded_file = st.file_uploader("Upload related file:", type=['jpg','jpeg','png'],accept_multiple_files=False)  
    if uploaded_file is not None:
        value_progress_bar=100
        st.write("Your file has been uploaded successfully.")
        st.write("No need to fear, we won't save it.")
        # Convert the file to an opencv image.
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        captured_image = cv2.imdecode(file_bytes, 1)
        # Recolor image back to BGR for rendering
        captured_image = cv2.cvtColor(captured_image, cv2.COLOR_RGB2BGR)
        st.image(captured_image,caption='Uploaded Image')
        if mediapipe_only(captured_image,class_name):
            st.write("Record created sucessfully.🙏")
            st.progress(100)

with click_tab:
    captured_image=st.camera_input("Capture an Image")
    if captured_image is not None:
        save_or_not=st.selectbox("Want to continue with this photo?", ("No","Yes", "Save this one, I will add another."))
        if save_or_not is not "No":
            mediapipe_only(captured_image,class_name)#==True:
            st.write("Record created sucessfully.🙏")
        else:
            st.write("Click 'Clear Photo below captured photograph to retake the photograph!'")