#!/usr/bin/env python3
###########################################################################
#    Lios - Linux-Intelligent-Ocr-Solution
#    Copyright (C) 2011-2015 Nalin.x.Linux GPL-3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

import os
import itertools

datadir = ''

def get_list_of_mixed_case_combinations(list_items):
    return list(itertools.chain.from_iterable(
        [[''.join(a) for a in itertools.product(*zip(s.upper(), s.lower()))] 
         for s in list_items]
    ))

user_home_path = os.environ['HOME']

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

config_dir = user_home_path + "/.lios"
tmp_dir = "/tmp/Lios/"
bookmarks_dir = config_dir + "/bookmarks/"

local_text_cleaner_list_file_path = config_dir + "/text_cleaner_list.text"
preferences_file_path = config_dir + "/preferences.cfg"
recent_file_path = config_dir + "/recent.text"
recent_cursor_position_file_path = config_dir + "/recent_cursor_position.text"

supported_image_formats = get_list_of_mixed_case_combinations(
    ["png","pnm","jpg","jpeg","tif","tiff","bmp","pbm","ppm"]
)
supported_text_formats = get_list_of_mixed_case_combinations(["txt","text"])
supported_pdf_formats = get_list_of_mixed_case_combinations(["pdf"])

version = "2.8"

# --- Default relative names ---
logo_file = "lios.png"
icon_dir = "icons/"
readme_file = "readme.text"
default_text_cleaner_list_file_path = "text_cleaner_list.text"

# --- Resolve resource paths ---
def _resolve_datadir():
    """Resolve datadir based on installation type."""
    global datadir, logo_file, icon_dir, readme_file, default_text_cleaner_list_file_path
    
    # Priority 1: Check if running from source tree (development)
    source_data = os.path.join(parent_dir, "share", "lios")
    if os.path.exists(os.path.join(source_data, "lios.png")):
        datadir = source_data
    # Priority 2: Check pip user install location
    elif os.path.exists(os.path.join(user_home_path, ".local", "share", "lios", "lios.png")):
        datadir = os.path.join(user_home_path, ".local", "share", "lios")
    # Priority 3: Check system-wide install
    elif os.path.exists("/usr/share/lios/lios.png"):
        datadir = "/usr/share/lios"
    # Priority 4: Check /usr/local (some distros)
    elif os.path.exists("/usr/local/share/lios/lios.png"):
        datadir = "/usr/local/share/lios"
    else:
        # Fallback: try system-wide path anyway
        datadir = "/usr/share/lios"
    
    # Set the resource paths
    logo_file = os.path.join(datadir, "lios.png")
    icon_dir = os.path.join(datadir, "icons")
    readme_file = os.path.join(datadir, "readme.text")
    default_text_cleaner_list_file_path = os.path.join(datadir, "text_cleaner_list.text")

# Run resolution at import time
_resolve_datadir()


app_name = "Linux-intelligent-ocr-solution"
app_name_abbreviated = "lios"

source_link = "https://gitlab.com/Nalin-x-Linux/lios-3"
home_page_link = "https://www.zendalona.com/lios"
video_tutorials_link = "https://www.youtube.com/playlist?list=PLn29o8rxtRe1zS1r2-yGm1DNMOZCgdU0i"

major_character_encodings_list = [
 'us_ascii', 'utf-8', 'iso_8859_1','latin1',
 'iso_8859_2', 'iso_8859_7', 'iso_8859_9', 'iso_8859_15', 'eucjp', 'euckr',
 'gb2312_80', 'gb2312_1980', 'windows_1251', 'windows_1252', 'windows_1253',
 'windows_1254', 'windows_1255', 'windows_1256', 'windows_1257', 'windows_1258',
 'shiftjis', 'windows_1256', 'big5_hkscs', 'big5_tw', 'tis620'
]

# --- Safe setter ---
def set_datadir(new_datadir):
    """Override datadir at runtime. Only applies if the new path exists."""
    global datadir, logo_file, icon_dir, readme_file
    global default_text_cleaner_list_file_path

    # Only override if the new datadir actually has the required files
    new_logo = os.path.join(new_datadir, "lios.png")
    if os.path.exists(new_logo):
        datadir = new_datadir
        logo_file = new_logo
        icon_dir = os.path.join(datadir, "icons")
        readme_file = os.path.join(datadir, "readme.text")
        default_text_cleaner_list_file_path = os.path.join(datadir, "text_cleaner_list.text")
