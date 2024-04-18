from tkinter import *
from PIL import Image, ImageTk  
import requests
import re
import apod_desktop
import datetime


# Initialize the image cache
apod_desktop.init_apod_cache()

# Function to handle button click event for downloading APOD
def download_apod():
    # Get the date from the entry field
    selected_date = entry_date.get()
    
    # Add your logic here to download the APOD for the selected date
    # For demonstration purposes, let's use the apod_desktop module to add APOD to the cache
    apod_date = datetime.datetime.strptime(selected_date, "%Y-%m-%d").date()
    apod_id = apod_desktop.add_apod_to_cache(apod_date)
    if apod_id != 0:
        print("APOD downloaded successfully for date:", selected_date)
    else:
        print("Failed to download APOD for date:", selected_date)

# Function to handle button click event for setting desktop background
def set_desktop_background():
    # Add your logic here to set the desktop background with the selected APOD image
    pass

def search_apod_archive():
    # Get the date from the entry field
    selected_date = entry_date.get()
    
    # Fetch the corresponding image from the APOD archive
    image_url = get_image_from_archive(selected_date)
    
    # Check if the image URL is valid
    if image_url:
        # Display the image
        display_image(image_url)

def get_image_from_archive(date):
    archive_url = 'https://apod.nasa.gov/apod/archivepixFull.html'
    
    response = requests.get(archive_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Search for the image URL in the HTML content of the archive page
        pattern = r'<a href="(?P<url>ap{}\.html)">[^<]*?</a>'.format(date.replace("-", ""))
        match = re.search(pattern, response.text)
        
        if match:
            # Extract the URL of the image
            image_relative_url = match.group('url')
            image_url = f'https://apod.nasa.gov/apod/{image_relative_url}'
            print("Image URL:", image_url)  # Print the extracted image URL
            return image_url
        else:
            print("Error: APOD not found for the selected date.")
    else:
        print("Failed to fetch APOD archive page.")


# Function to display the image
def display_image(image_url):
    # Fetch the image data
    response = requests.get(image_url)
    
    if response.status_code == 200:
        # Convert the image data into a Tkinter PhotoImage
        # Load and display the NASA logo image
            nasa_logo_image = Image.open("C:/Users/micha/OneDrive/Documents/Comp593-Lab6-main/Comp593-FinalProject/images/NASA_logo.png")
            nasa_logo_image = nasa_logo_image.resize((200, 200))  # Resize the image
            nasa_logo_photo = ImageTk.PhotoImage(nasa_logo_image)

        # Display the image in a label
            image_label.configure(image=nasa_logo_photo)
            image_label.image = nasa_logo_photo
    else:
        print("Failed to fetch image from URL:", image_url)

# Create the GUI
root = Tk()
root.geometry('1000x800')
root.title("Astronomy Picture of the Day Viewer")

# Create and position widgets
label_date = Label(root, text="Select Date:")
label_date.grid(row=0, column=0, padx=50, pady=50)

entry_date = Entry(root, width=20)  # Increase width to 20 characters
entry_date.grid(row=0, column=1, padx=50, pady=50)

button_search_apod = Button(root, text="Type A Date then Click Me", command=search_apod_archive)
button_search_apod.grid(row=0, column=2, padx=10, pady=10, sticky="w")

button_download_apod = Button(root, text="Download", command=download_apod)
button_download_apod.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="w")

button_set_background = Button(root, text="Set as Background", command=set_desktop_background)
button_set_background.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")

# Create a label to display the image
image_label = Label(root)
image_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Load and display the NASA logo image
nasa_logo_image = Image.open("C:/Users/micha/OneDrive/Documents/Comp593-Lab6-main/Comp593-FinalProject/images/NASA_logo.png")
nasa_logo_image = nasa_logo_image.resize((600, 600))
nasa_logo_photo = ImageTk.PhotoImage(nasa_logo_image)
nasa_logo_label = Label(root, image=nasa_logo_photo)
nasa_logo_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Configure columns to resize with window
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

# Configure bottom left alignment for the buttons
root.grid_rowconfigure(4, weight=1)

root.mainloop()
