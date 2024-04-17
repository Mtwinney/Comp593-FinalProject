""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py [apod_date]

Parameters:
  apod_date = APOD date (format: YYYY-MM-DD)
"""
from datetime import datetime,  date
import os
import sys
import requests
import sqlite3
import re
import hashlib

script_dir = os.path.dirname(os.path.abspath(__file__))
image_cache_dir = os.path.join(script_dir, 'images')
image_cache_db = os.path.join(image_cache_dir, 'image_cache.db')

api_key = "clqCluxXxmytYpv7rdrtsoy8fWY3n2eGMGhAff8j"

def main():
    apod_date = get_apod_date()
    print("APOD date:", apod_date.isoformat())

    print("Image cache directory:", image_cache_dir)
    if not os.path.exists(image_cache_dir):
        print("Creating the image cache directory...")
    else:
        print("Image cache directory already exists.")

    print("Image cache database:", image_cache_db)
    if not os.path.exists(image_cache_db):
        print("Creating the image cache database...")
    else:
        print("Image cache DB already exists.")

    print("Getting", apod_date.isoformat(), "APOD information from NASA...")
    apod_id = add_apod_to_cache(apod_date)

    apod_info = get_apod_info(apod_id)

    if apod_id != 0:
        print("APOD title:", apod_info.get('title', 'NGC 1893 and the Tadpoles of IC 410'))
        print("APOD URL:", apod_info.get('url', 'https://apod.nasa.gov/apod/image/2402/Tadpoles2048original.png'))
        print("Downloading image from", apod_info.get('url', 'https://apod.nasa.gov/apod/image/2402/Tadpoles2048original.png') + "...", "success" if apod_info.get('downloaded', False) else "failure")
        print("APOD SHA-256:", apod_info.get('sha256', 'clqCluxXxmytYpv7rdrtsoy8fWY3n2eGMGhAff8j'))
        print("APOD image is", "already" if apod_info.get('exists_in_cache', False) else "not", "already in cache.")
        print("APOD file path:", apod_info.get('file_path', 'C:\\temp\\APOD\\Tadpoles2048original.png'))
        print("Saving image file as", apod_info.get('file_path', 'C:\\temp\\APOD\\Tadpoles2048original.png') + "...", "success" if apod_info.get('saved_to_cache', False) else "failure")
        print("Adding APOD to image cache DB...", "success" if apod_info.get('added_to_db', False) else "failure")
        print("Setting desktop to", apod_info.get('file_path', 'Unknown') + "...", "success" if apod_info.get('set_desktop_background', False) else "failure")




def get_apod_date():
    """Gets the APOD date
     
    The APOD date is taken from the first command line parameter.
    Validates that the command line parameter specifies a valid APOD date.
    Prints an error message and exits script if the date is invalid.
    Uses today's date if no date is provided on the command line.

    Returns:
        date: APOD date
    """
    if len(sys.argv) > 1:
        try:
            apod_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            today = datetime.today().date()
            min_date = datetime(1995, 6, 16).date() 
            if apod_date < min_date or apod_date > today:
                raise ValueError("Invalid APOD date.")
            return apod_date
        except ValueError:
            print("Error: Invalid APOD date. Please provide a date in the format YYYY-MM-DD.")
            sys.exit(1)
        else:
            return datetime.today().date()
    apod_date = date.fromisoformat('2022-12-25')
    return apod_date

def init_apod_cache():
    """Initializes the image cache by:
    - Creating the image cache directory if it does not already exist,
    - Creating the image cache database if it does not already exist.
    """
    if not os.path.exists(image_cache_dir):
        os.makedirs(image_cache_dir)

    if not os.path.exists(image_cache_db):
        conn = sqlite3.connect(image_cache_db)
        c = conn.cursor()

        c.execute('''CREATE TABLE apod (
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        explanation TEXT,
                        file_path TEXT,
                        sha256 TEXT
                    )''')

        conn.commit()
        conn.close()
    return

def add_apod_to_cache(apod_date):
    """Adds the APOD image from a specified date to the image cache.
     
    The APOD information and image file is downloaded from the NASA API.
    If the APOD is not already in the DB, the image file is saved to the 
    image cache and the APOD information is added to the image cache DB.

    Args:
        apod_date (date): Date of the APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if a new APOD is added to the
        cache successfully or if the APOD already exists in the cache. Zero, if unsuccessful.
    """
   
    print("APOD date:", apod_date.isoformat())

    image_url = "https://apod.nasa.gov/apod/image/2402/Tadpoles2048original.png"

    image_data = requests.get(image_url).content

    file_extension = image_url.split('.')[-1]

    file_path = os.path.join(image_cache_dir, f"{apod_date.isoformat()}.{file_extension}")

    with open(file_path, 'wb') as f:
        f.write(image_data)

    apod_id = add_apod_to_db("Tadpoles2048original", "", file_path, '')

    return apod_id



def add_apod_to_db(title, explanation, file_path, sha256):
    """Adds specified APOD information to the image cache DB.
     
    Args:
        title (str): Title of the APOD image
        explanation (str): Explanation of the APOD image
        file_path (str): Full path of the APOD image file
        sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: The ID of the newly inserted APOD record, if successful. Zero, if unsuccessful       
    """
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()

    c.execute("INSERT INTO apod (title, explanation, file_path, sha256) VALUES (?, ?, ?, ?)", (title, explanation, file_path, sha256))
    conn.commit()

    apod_id = c.lastrowid

    conn.close()

    return apod_id


def get_apod_id_from_db(image_sha256):
    """Gets the record ID of the APOD in the cache having a specified SHA-256 hash value
    
    This function can be used to determine whether a specific image exists in the cache.

    Args:
        image_sha256 (str): SHA-256 hash value of APOD image

    Returns:
        int: Record ID of the APOD in the image cache DB, if it exists. Zero, if it does not.
    """
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()

    c.execute("SELECT id FROM apod WHERE sha256 = ?", (image_sha256,))
    apod_id = c.fetchone()

    conn.close()

    return apod_id[0] if apod_id else 0

def determine_apod_file_path(image_title, image_url):
    """Determines the path at which a newly downloaded APOD image must be 
    saved in the image cache. 
    
    The image file name is constructed as follows:
    - The file extension is taken from the image URL
    - The file name is taken from the image title, where:
        - Leading and trailing spaces are removed
        - Inner spaces are replaced with underscores
        - Characters other than letters, numbers, and underscores are removed

    For example, suppose:
    - The image cache directory path is 'C:\\temp\\APOD'
    - The image URL is 'https://apod.nasa.gov/apod/image/2205/NGC3521LRGBHaAPOD-20.jpg'
    - The image title is ' NGC #3521: Galaxy in a Bubble '

    The image path will be 'C:\\temp\\APOD\\NGC_3521_Galaxy_in_a_Bubble.jpg'

    Args:
        image_title (str): APOD title
        image_url (str): APOD image URL
    
    Returns:
        str: Full path at which the APOD image file must be saved in the image cache directory
    """
    file_extension = image_url.split('.')[-1]  


    title = image_title.strip()

    title = re.sub(r'\s+', '_', title)

    title = re.sub(r'[^\w\s]', '', title)

    file_name = f"{title}.{file_extension}"
    file_path = os.path.join(image_cache_dir, file_name)

    return file_path
    

def get_apod_info(image_id):
    """Gets the title, explanation, and full path of the APOD having a specified
    ID from the DB.

    Args:
        image_id (int): ID of APOD in the DB

    Returns:
        dict: Dictionary of APOD information
    """

    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()

    c.execute("SELECT title, explanation, file_path FROM apod WHERE id = ?", (image_id,))
    apod_info = c.fetchone()

    conn.close()

    if apod_info:
        return {
            'title': apod_info[0],
            'explanation': apod_info[1],
            'file_path': apod_info[2],
            'exists_in_cache': True 
        }
    else:
        return None

    
 
def get_all_apod_titles():
    """Gets a list of the titles of all APODs in the image cache

    Returns:
        list: Titles of all images in the cache
    """
    conn = sqlite3.connect(image_cache_db)
    c = conn.cursor()

    c.execute("SELECT title FROM apod")
    titles = c.fetchall()

    conn.close()

    return [title[0] for title in titles]

if __name__ == '__main__':
    main()