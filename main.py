###################################
#     Importing dependencies      #
###################################

import streamlit as st
import mediapipe as mp 
import cv2 
import csv
import numpy as np
from PIL import Image,ImageOps
from streamlit_webrtc import webrtc_streamer
import av
import os
from streamlit_fesion import streamlit_fesion

mp_drawing = mp.solutions.drawing_utils 
mp_holistic = mp.solutions.holistic 

class_name='Unassigned'

path_of_csv='coords.csv' 

###################################
#       Classes & Functions       #
###################################


###################################
#       Necessary Functions       #
###################################

def is_empty_csv(path):
    with open(path) as csvfile:
        reader = csv.reader(csvfile)
        for i, _ in enumerate(reader):
            if i:  # found the second row
                return False
    return True
def add_column_header(path):
    if is_empty_csv(path):
        landmarks = ['class']
        for val in range(1, 502):
            landmarks += ['x{}'.format(val), 'y{}'.format(val), 'z{}'.format(val), 'v{}'.format(val)]
        with open(path, mode='w', newline='') as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(landmarks)
    else:
        pass




def mediapipe_only(image:str, class_name:str):
  #try:
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
            if len(row)>0:
            # Export to CSV
                with open('coords.csv', mode='a', newline='') as f:
                    csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    csv_writer.writerow(row)
                    #st.header("adding the row") 
            else:
                st.write("Didn't write blank row to csv")
        except:
            st.error(str="Failed to write CSV",icon="🚨")
    return True
  #except:
    #return False
       
def get_class():
    return class_name  

def video_frame_callback(frame):
    class_name=get_class()
    captured_image = frame.to_ndarray(format="bgr24")
    try: 
        mediapipe_only(captured_image,class_name)# == True:
        st.write("Record created sucessfully.🙏")
    except:
        pass
    return av.VideoFrame.from_ndarray(captured_image, format="bgr24")

def image_filter(input_image):
    import skimage
    class_name=get_class()
    grayscale = skimage.color.rgb2gray(input_image)
    mediapipe_only(input_image,class_name)# == True:
    st.write("Record created sucessfully.🙏")
    
    return skimage.color.gray2rgb(grayscale)


def page_configurations():
    st.set_page_config(page_title="Dataset Creator", page_icon=":tada:", layout="wide", initial_sidebar_state="auto", menu_items={"Get Help":"https://github.com/kushagrathisside/Dataset-Creator","About":"https://www.linkedin.com/in/kushagrathisside"})



###################################
#   STARTING THE WEBPAGE CODE     #
###################################
def main():
    #set page config
    page_configurations()
    
    #writing on the screen
    st.title("DATASET GENERATOR")
    
    #'''
    #Relevant links: 
    #https://blog.sparkhire.com/2012/12/17/facial-expressions-in-video-interview/#:~:text=Facial%20expressions%20carry%20as%20much%20weight%20as%20strong,to%20toe%20that%20line%20between%20confident%20and%20creepy.
    #https://www.communicationtheory.org/importance-of-facial-expressions-in-communication/
    #https://harappa.education/harappa-diaries/types-of-facial-expression-in-communication/
    #'''
    
    class_name = st.selectbox(
        "Which emotion do you want to show?",
        ("Happiness", "Sadness", "Anger","Fear","Disgust","Confused","Contempt","Thoughful","Shy","Surprised","Excited")
    )
    
    #check if file is present or not. If file(csv) is not present then it is first created, and then column headers are added.
    if os.path.isfile(path_of_csv):
        add_column_header(path_of_csv)
    else:
        with open(path_of_csv, mode='w', newline='') as f:
            f.close()
            add_column_header(path_of_csv)


    #Creating Parallel Tabs as options for user 
    upload_tab, click_tab, livewebcam = st.tabs(["Upload", "Click a picture", "Live Camera"])
    with upload_tab:
        value_progress_bar=0
        my_bar = st.progress(value_progress_bar)
        uploaded_file = st.file_uploader("Upload related file:", type=['jpg','jpeg','png'],accept_multiple_files=False)
        #print("uploaded",type(uploaded_file))  
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
        captured_image = st.camera_input("Capture an Image")
        if captured_image is not None:
            save_or_not=st.selectbox("Want to continue with this photo?", ("No","Yes"))
            #st.write(save_or_not)
            #Captured stream to Image
            captured_image=Image.open(captured_image)
            captured_image = np.array(captured_image)
            #captured_image = cv2.cvtColor(captured_image, cv2.COLOR_RGB2BGR)
        
            #Task: To read image file buffer with OpenCV
            #Alternate Solution:
            #    bytes_data = img_file_buffer.getvalue()
            #    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

            if save_or_not == "Yes":
                mediapipe_only(captured_image,class_name)# == True:
                st.write("Record created sucessfully.🙏")
            else:
                st.write("Change the 'No' option visible above to add new row.")
            
    with livewebcam:
        #livefeed = webrtc_streamer(key="sample", video_frame_callback=video_frame_callback)
        st.header("Under Construction 🚧")
        streamlit_fesion(image_filter, [], key="fesion")


#main function
if __name__=="__main__":
    main()
