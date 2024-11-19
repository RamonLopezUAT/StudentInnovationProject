# Application Version: 11.18.2024

import tkinter as tk
import os, datetime, shutil, piexif, ctypes
from tkinter import filedialog, messagebox, PhotoImage
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

# Global variable to store metadata
metadata = {}

# Update Status
def update_status(message):
    status_label.config(text=message)
    root.update_idletasks() # Allows the UI to update

# Open File Explorer
def open_file_explorer():
    file_path = filedialog.askopenfilename()
    if file_path:
        switch_to_resultspage(file_path)
    else:
        messagebox.showinfo("Information", "No file selected")

# Copy File
def copy_file_with_metadata(file_path):
    folder_path = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    new_file_path = os.path.join(folder_path, f'copy_of_{filename}')
    shutil.copy2(file_path, new_file_path)
    return new_file_path

def remove_metadata(file_path):
    file_type = os.path.splitext(file_path)[1].lower()
    if file_type in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
        remove_image_metadata(file_path)
    else:
        print("Metadata removal is not supported for this file type.")

# Function to remove image metadata (EXIF)
def remove_image_metadata(file_path):
    try: # Notify the user that the process is starting
        messagebox.showinfo("Removing Metadata", "Starting metadata removal...")
        image = Image.open(file_path)
        
        # Check for EXIF metadata
        if 'exif' in image.info:
            exif_data = image.info['exif']
            exif_dict = piexif.load(exif_data)
            if exif_dict: # Clear the EXIF dictionary
                exif_dict.clear()
                exif_bytes = piexif.dump(exif_dict)
                
                # Save the image without EXIF metadata
                output_path = file_path.replace(".", "_without_metadata.")
                image.save(output_path, exif=exif_bytes)

                # Notify the user of successful removal
                messagebox.showinfo("Success", f"Metadata removed successfully! File saved as {output_path}")
            else: # Notify the user that no metadata was found
                messagebox.showinfo("No Metadata", "No EXIF metadata found in the image.")
        else: # Final check using piexif in case PIL missed the EXIF tag
            exif_dict = piexif.load(file_path)
            if exif_dict:
                exif_dict.clear()
                exif_bytes = piexif.dump(exif_dict)
                output_path = file_path.replace(".", "_no_metadata.")
                image.save(output_path, exif=exif_bytes)
                messagebox.showinfo("Success", f"Metadata removed successfully! File saved as {output_path}")
            else:
                messagebox.showinfo("No Metadata", "No EXIF metadata found in the image.")
    except Exception as e:
        messagebox.showerror("Error", f"Error removing metadata: {e}")

# Switch to the different pages
def switch_to_resultspage(file_path):
    homepage_frame.pack_forget()
    resultspage_frame.pack()
    update_status("Loading file...")
    display_preview(file_path)
    display_metadata(file_path)
    selected_file_label.config(text=file_path)
    update_status("File loaded successfully.")

def switch_to_homepage():
    resultspage_frame.pack_forget()
    homepage_frame.pack()
    update_status("Ready.")

# Display Preview (for images)
def display_preview(file_path):
    try:
        preview_image = Image.open(file_path)
        preview_image.thumbnail((600, 200))
        preview_photo = ImageTk.PhotoImage(preview_image)
        preview_label.config(image=preview_photo)
        preview_label.image = preview_photo
    except Exception:
        preview_label.config(text="No preview available for this file type.")

# Display Metadata based on file type
def display_metadata(file_path):
    global metadata
    file_name = os.path.basename(file_path)
    file_type = os.path.splitext(file_path)[1].lower()  # Make sure to compare lowercase extensions
    
    # Initialize metadata dictionary
    metadata = {
        "File Name": file_name,
        "File Type": file_type,
        "File Size (bytes)": " - ",
        "Created Time": " - ",
        "Modified Time": " - ",
    }
    
    # Try to get general file properties (size, created, modified times)
    try:
        metadata["File Size (bytes)"] = os.path.getsize(file_path)
        created_time = os.path.getctime(file_path)
        metadata["Created Time"] = datetime.datetime.fromtimestamp(created_time).strftime('%Y-%m-%d %H:%M:%S')
        modified_time = os.path.getmtime(file_path)
        metadata["Modified Time"] = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error extracting general metadata: {e}")

    # Handle different file types
    if file_type in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
        extract_image_metadata(file_path)
    else:
        print("Unsupported file type for metadata extraction")

    # Display metadata on the UI
    display_text = ""
    for key, value in metadata.items():
        if show_empty_metadata.get() or value != " - ":
            display_text += f"{key}: {value} ({get_explanation(key)})\n"
    metadata_label.config(text=display_text)

# Function to extract image metadata
def extract_image_metadata(file_path):
    try:
        image = Image.open(file_path)
        image_size = image.size
        image_orientation = image.info.get('exif', {}).get(0x0112, " - ")
        dots_per_inch = image.info.get('dpi', " - ")
        exif_data = piexif.load(image.info['exif']) if 'exif' in image.info else {}
        gps_info = exif_data.get("GPS", {})
        GPS_Latitude = gps_info.get(0x0002, " - ")
        GPS_Longitude = gps_info.get(0x0004, " - ")
        GPS_Altitude = gps_info.get(0x0006, " - ")
        Software = exif_data.get("0th", {}).get(piexif.ImageIFD.Software, " - ")
        metadata.update({
            "Image Size": image_size,
            "Image Orientation": image_orientation,
            "Dots Per Inch": dots_per_inch,
            "GPS Latitude": GPS_Latitude,
            "GPS Longitude": GPS_Longitude,
            "GPS Altitude": GPS_Altitude,
            "Software": Software
        })
    except Exception as e:
        print(f"Error extracting image metadata: {e}")

# Function that adds the explanations to the files
def get_explanation(key):
    explanations = {
        "File Name": "Name of the file",
        "File Type": "Type of the file, e.g., .jpg, .png",
        "File Size (bytes)": "Size of the file in bytes",
        "Image Size": "Dimensions of the image in pixels",
        "Image Orientation": "Orientation of the image, e.g., landscape, portrait",
        "Dots Per Inch": "Dots per inch, resolution of the image",
        "Created Time": "Date and time when the file was created",
        "Modified Time": "Date and time when the file was last modified",
        "GPS Latitude": "Latitude where the photo was taken",
        "GPS Longitude": "Longitude where the photo was taken",
        "GPS Altitude": "Altitude where the photo was taken",
        "Software": "Software used to process the image"
    }
    return explanations.get(key, "")

# Function that exports the metadata
def export_metadata():
    global metadata
    if metadata:
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]) # This allows the metadata to be saved as a .txt file
        if save_path:
            with open(save_path, 'w') as file: # Saves the metadata in the chosen path with "write" permissions.
                for key, value in metadata.items():
                    file.write(f"{key}: {value}\n")
            messagebox.showinfo("Information", "Metadata exported successfully.") # SUCCESS!
        else:
            messagebox.showinfo("Information", "Export cancelled.") # Something went wrong?
    else:
        messagebox.showinfo("Information", "No metadata to export.") # No Metadata!

# Drag and drop frame gets created here
def drop(event):
    file_path = event.data.strip('{}')
    if file_path and os.path.isfile(file_path):
        switch_to_resultspage(file_path)
    else:
        messagebox.showinfo("Information", "No valid file dropped")

# Sets up the green header for both the homepage and resultspage
def create_header(frame):
    header = tk.Label(frame, text="Meta Insight", bg="green", fg="white", font=("Arial", 16), width=100, height=1)
    header.pack(side="top", fill="x", anchor="n")  # Fill the width of the frame
    return header

# Set up main Tkinter window with TkinterDnD
root = TkinterDnD.Tk()

# Sets up the logo on both the window and taskbar
logo_path = "Meta_Insight(Short_Logo).ico"  # Replace with the actual path to your logo file
if os.name == 'nt': # This will looks to see if you have the Windows operating system
    myappid = 'Student Innovation Project.Meta Insight.11.18.2024' # This prevent the program to open its default logo.
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    root.iconbitmap(logo_path)  # Replace the tkinter default logo

root.title("MetaInsight: An Educational Metadata Extraction Tool | Build: 11.18.2024")
SCREENWIDTH = root.winfo_screenwidth()
SCREENHEIGHT = root.winfo_screenheight()
root.geometry(f"{SCREENWIDTH}x{SCREENHEIGHT}")

'''This section creates and maintains the homepage, anything that needs to go into the homepage goes here'''
homepage_frame = tk.Frame(root)

# Creates the header bar in the Resultpage
homepage_frame.pack()
homepage_header = create_header(homepage_frame) # Add the header to the homepage frame

# Drop target for drag and drop
drop_target = tk.Label(homepage_frame, text="Drag and Drop Files Here", width=95, height=20, bg="lightblue")
drop_target.pack(pady=50)
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)
selected_file_label = tk.Label(homepage_frame, text="", font=("Arial", 12))
selected_file_label.pack()
open_button = tk.Button(homepage_frame, text="Open File Explorer", command=open_file_explorer)
open_button.pack()

'''This section creates and maintains the resultspage, anything that needs to go into the resultspage goes here'''
resultspage_frame = tk.Frame(root)

# Creates the header bar in the Resultpage
results_header = create_header(resultspage_frame) # Add the header to the resultspage frame
status_label = tk.Label(resultspage_frame, text="", font=("Arial", 10), fg="green")
status_label.pack(pady=5)  # Add some padding

# Creates the preview page for Images
preview_frame = tk.Frame(resultspage_frame, width=SCREENWIDTH, height=300, bg="lightgray")
preview_frame.pack()
preview_label = tk.Label(preview_frame)
preview_label.pack(padx=10, pady=10)

# Creates the frame where metadata is shown.
metadata_frame = tk.Frame(resultspage_frame)
metadata_frame.pack()
metadata_width = 55
metadata_height = 10
metadata_label = tk.Label(resultspage_frame, font=("Arial", 8))
metadata_label.pack()

# Creates a frame to store the options users have to do.
button_frame = tk.Frame(resultspage_frame)
button_frame.pack(pady=10)  # Add padding for spacing and center alignment
button_frame.pack(anchor="center") # Centers the frame to the middle

# Checkbox to toggle visibility of empty metadata
show_empty_metadata = tk.BooleanVar()
show_empty_metadata.set(True)  # By default, show all metadata

# Section to show the empty Metadata box
toggle_empty_metadata_checkbox = tk.Checkbutton(button_frame, text="Show Empty Metadata", variable=show_empty_metadata, command=lambda: display_metadata(selected_file_label.cget("text")))
toggle_empty_metadata_checkbox.pack(side=tk.LEFT, padx=5, pady=5)

# This creates the button for the "Open Another File".
back_button = tk.Button(button_frame, text="Open Another File", width=13, command=switch_to_homepage)
back_button.pack(side=tk.LEFT, padx=5, pady=5)

# This creates the button for the "Remove Metadata".
remove_metadata_button = tk.Button(button_frame, text="Remove Metadata", width=13, command=lambda: remove_metadata(selected_file_label.cget("text")))
remove_metadata_button.pack(side=tk.LEFT, padx=5, pady=5)

# This creates the button for the "Export Metadata".
export_metadata_button = tk.Button(button_frame, text="Export Metadata", width=13, command=export_metadata)
export_metadata_button.pack(side=tk.LEFT, padx=5, pady=5)

root.mainloop()