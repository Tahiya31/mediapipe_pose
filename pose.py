'''

This script is written to extract 33 body key points (x, y, z, visbility) from a video containing one person in it using mediapipe.
Example scenario is a Zoom video recording with one people in it.

To use this for your data analysis:
  - Create a folder called 'input_videos' in the same folder where this script is, and put your input videos in that folder.
  - Go to Terminal (MAC) or Commant Prompt (Windows) and run `python pose.py` to this script. (It is best to test on one file first, check if everything looks ok, 
  and then run on all your files in a single batch)
  - Once the script runs through all the videos files, check in the output folder for your csv files.


'''

#import packages/libraries
import cv2
import mediapipe as mp
import csv
import os
import sys

# Function to install mediapipe if not already installed
def install_mediapipe():
    try:
        import mediapipe as mp
    except ImportError:
        print("Mediapipe not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe"])
        import mediapipe as mp  # Import after installation
    return mp

# Ensure mediapipe is installed
mp = install_mediapipe()


# Set up GPU environment for Mediapipe (specific for Saturn Cloud), if you use some other high performance computing platform check compatibility before usage
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # Make sure the system uses the GPU

# Initialize Mediapipe Pose module with GPU support
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1) # Complexity 1 for better GPU utilization

mp_drawing = mp.solutions.drawing_utils

# List of Mediapipe pose landmarks, from https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/pose.md
landmark_names = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer", "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right", "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_pinky", "right_pinky", "left_index",
    "right_index", "left_thumb", "right_thumb", "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel", "left_foot_index", "right_foot_index"
]

# Function to process video and extract keypoints using GPU
def extract_keypoints_from_video_gpu(video_path, output_csv):
  
  # Open video file
  cap = cv2.VideoCapture(video_path)

  # Check if video opened successfully
  if not cap.isOpened():
    print(f"Error opening video file {video_path}")
    return

  # Prepare CSV file for writing
  with open(output_csv, mode='w', newline='') as file:
    csv_writer = csv.writer(file)

    # Write the header row for CSV
    header = ['frame'] + [f'{landmark}_{coord}' for landmark in landmark_names for coord in ['x', 'y', 'z', 'visibility']]
    csv_writer.writerow(header)

    frame_idx = 0
    while cap.isOpened():
      success, frame = cap.read()
      if not success:
        break  # End of video

      # Convert the image from BGR to RGB (as Mediapipe uses RGB)
      rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

      # Process the frame with Mediapipe Pose (on GPU)
      result = pose.process(rgb_frame)

      # Check if any keypoints are detected
      if result.pose_landmarks:
        landmarks = result.pose_landmarks.landmark

        # Extract keypoints (x, y, z, visibility) for each landmark
        keypoints = []
        for landmark in landmarks:
          keypoints.append(landmark.x)
          keypoints.append(landmark.y)
          keypoints.append(landmark.z)
          keypoints.append(landmark.visibility)

        # Write the frame number and keypoints to the CSV
        csv_writer.writerow([frame_idx] + keypoints)

      frame_idx += 1

  # Release the video capture object
  cap.release()
  print(f'Keypoints extracted and saved to {output_csv}')


# Function to process all videos in a folder
def process_videos_in_folder(input_folder, output_folder):
  # Ensure output folder exists, if not create one
  if not os.path.exists(output_folder):
    os.makedirs(output_folder)

  # Loop through all video files in the input folder
  for video_file in os.listdir(input_folder):
    if video_file.endswith('.mp4') or video_file.endswith('.avi'):  # Adjust based on video formats
      video_path = os.path.join(input_folder, video_file)
      output_csv = os.path.join(output_folder, video_file.replace('.mp4', '.csv').replace('.avi', '.csv'))

      print(f"Processing video: {video_file}")
      extract_keypoints_from_video_gpu(video_path, output_csv)



# input_folder: folder where your input video files are
# output_folder: folder where output files will be, if it does not exist on the first run, the script will create a folder with this name
input_folder = 'input_videos'  # Replace with your folder containing video files
output_folder = 'output_keypoints'  # Folder where CSVs will be saved

# Process all videos in the input folder
process_videos_in_folder(input_folder, output_folder)
