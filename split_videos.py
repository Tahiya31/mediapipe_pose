'''

This script is written to split a video with two people in separate screen at midpoint (or user-defined splitting point) to get to separate videos with one person in each.
Example scenario is a Zoom video recording with two people.

To use this for your data analysis:
  - Create a folder called 'input_videos' in the same folder where this script is, and put your input videos in that folder.
  - Go to Terminal (MAC) or Commant Prompt (Windows) and run `python split_videos.py` to this script. (It is best to test on one file first, check if everything looks ok, 
  and then run on all your files in a single batch)
  - Once the script runs through all the videos files, check in the output folder for your split videos (total input files * 2)


'''


#import packages, libraries
import os
import subprocess

# function to split the screen from the midpoint
def split_video_vertically(input_folder, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each MP4 file in the input folder
    for video_file in os.listdir(input_folder):
        if video_file.endswith(".mp4"):
            input_path = os.path.join(input_folder, video_file)
            output_file_A = os.path.join(output_folder, video_file.replace('.mp4', '_A.mp4'))
            output_file_B = os.path.join(output_folder, video_file.replace('.mp4', '_B.mp4'))

            # Get video dimensions using ffprobe (width and height)
            command_dimensions = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x \"{input_path}\""
            dimensions = subprocess.check_output(command_dimensions, shell=True).decode().strip()
            width, height = map(int, dimensions.split('x'))
            midpoint = (width // 2) + 20 # Calculate the midpoint for splitting, the true splitting point was not at the midpoint, so added an extra 20 pixel for right shift

            # Create two split videos using the crop filter
            # left half (A)
            command_A = f"ffmpeg -i \"{input_path}\" -vf \"crop={midpoint}:{height}:0:0\" -c:a copy \"{output_file_A}\""
            subprocess.call(command_A, shell=True)

            # right half (B)
            command_B = f"ffmpeg -i \"{input_path}\" -vf \"crop={midpoint}:{height}:{midpoint}:0\" -c:a copy \"{output_file_B}\""
            subprocess.call(command_B, shell=True)

            print(f"Video {video_file} split into {output_file_A} (left half) and {output_file_B} (right half)")


# input_folder: folder where your input video files are
# output_folder: folder where output files will be, if it does not exist on teh first run, the script will create a folder with this name
input_folder = "input_videos"  # Folder with input videos
output_folder = "output_split_videos"  # Folder where split videos will be saved

split_video_vertically(input_folder, output_folder)