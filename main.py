import cv2
import os

# Keep input_video_path
input_video_path = r"C:\Users\ASUS\Desktop\PythonDataAnnotation\Data_anonymization\SourceClips\05.03.2025\20250305_17_10_10_Pro_FTS1.mp4"

# Extract filename and generate output path dynamically
input_filename = os.path.basename(input_video_path)  # Extract "20250305_15_22_15_Pro_FTS1.mp4"
name, ext = os.path.splitext(input_filename)  # Split into "20250305_15_22_15_Pro_FTS1" and ".mp4"

# Define output folder
output_folder = r"C:\Users\ASUS\Desktop\PythonDataAnnotation\Data_anonymization\anonymized\06.03.2025"

# Generate dynamic output filename
output_video_path = os.path.join(output_folder, f"BlackedOut{input_filename}")

# Open video
cap = cv2.VideoCapture(input_video_path)
if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Get original video properties
orig_fps = cap.get(cv2.CAP_PROP_FPS)
orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Get your screen resolution (Office Laptop)
screen_width = 1920
screen_height = 1080

# Calculate best fit for display
scale_factor = min(screen_width / orig_width, screen_height / orig_height)
display_width = int(orig_width * scale_factor)
display_height = int(orig_height * scale_factor)

# Variables for mouse selection
x1, y1, x2, y2 = -1, -1, -1, -1
drawing = False
selected = False  

def draw_rectangle(event, x, y, flags, param):
    global x1, y1, x2, y2, drawing, selected

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x1, y1 = x, y
        x2, y2 = x, y  

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            x2, y2 = x, y  

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        selected = True  
        x2, y2 = x, y
        print(f"Selected blackout area (scaled): ({x1}, {y1}) to ({x2}, {y2})")

# Get first frame for selection
ret, first_frame = cap.read()
if not ret:
    print("Error: Could not read first frame.")
    cap.release()
    exit()

# Resize frame for display
first_frame_resized = cv2.resize(first_frame, (display_width, display_height))

cv2.namedWindow('Select Blackout Area', cv2.WINDOW_NORMAL)  # Allow window resizing
cv2.setMouseCallback('Select Blackout Area', draw_rectangle)

# Selection loop
while True:
    temp_frame = first_frame_resized.copy()
    if drawing or selected:
        cv2.rectangle(temp_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow('Select Blackout Area', temp_frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and selected:
        print("Selection confirmed. Processing video...")
        break
    elif key == ord('q'):
        print("Selection cancelled by user.")
        cap.release()
        cv2.destroyAllWindows()
        exit()

cv2.destroyWindow('Select Blackout Area')

# Convert coordinates to original resolution
x1, y1 = round(x1 / scale_factor), round(y1 / scale_factor)
x2, y2 = round(x2 / scale_factor), round(y2 / scale_factor)
print(f"Blackout area in original resolution: ({x1}, {y1}) to ({x2}, {y2})")

# Video writer (MP4 format, no additional codec needed)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_video_path, fourcc, orig_fps, (orig_width, orig_height))

frame_count = 0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Process video
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply blackout
    frame[y1:y2, x1:x2] = (0, 0, 0)

    # Write to output file
    out.write(frame)

    frame_count += 1
    print(f"Processing: {frame_count}/{total_frames} frames", end='\r')

cap.release()
out.release()

print("\n✅ Video saved successfully!")
