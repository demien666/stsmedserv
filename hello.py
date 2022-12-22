from flask import Flask, render_template, url_for
from typing import Tuple, List
import os
from dataclasses import dataclass

URI_PATH_SEP = "->"
URI_SPACE = "___"
PATH_SEP = "/"
BASE_PATH = "/home/dmitry"
VID_EXT = [".avi", ".mkv", ".mp4"]


@dataclass
class FileInfo:
    path: str
    name: str

app = Flask(__name__, static_folder=BASE_PATH)

def uri_to_path(uri: str) -> str:
    return uri.replace(URI_PATH_SEP, PATH_SEP).replace(URI_SPACE, " ")

def path_to_uri(path: str) -> str:
    return path.replace(PATH_SEP, URI_PATH_SEP).replace(" ", URI_SPACE)

def is_video_file(name: str) -> bool:
    filtered = [v for v in VID_EXT if v in name]
    return len(filtered) > 0

def remove_file_extension(name: str) -> str:
    result = name
    for ext in VID_EXT:
        result = result.replace(ext, "")
    return result    

def get_folders_and_files(dir_path: str) -> Tuple[List[FileInfo], List[FileInfo]]:
    folders = []
    files = []
    for file_name in os.listdir(dir_path):
        full_path = os.path.join(dir_path, file_name)
        static_path = "../play/" + path_to_uri(full_path.replace(BASE_PATH, ""))
        file_info = FileInfo(static_path, remove_file_extension(file_name))
        # check if current path is a file
        if os.path.isfile(full_path):
            if is_video_file(file_name):
                files.append(file_info)
        else:
            folders.append(file_info)
    return folders, files         

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/play/<uri>")
def play(uri):
    path = uri_to_path(uri)
    print(path)
    return render_template('video.html', video_path=path)

@app.route("/folder/<uri>")
def folder(uri=""):
    path = uri_to_path(uri)
    full_path = os.path.join(BASE_PATH, path)
    (folders, files) =  get_folders_and_files(full_path)
    print(path)
    return render_template('folder.html', folders=folders, files=files)    

@app.route('/content/<level1>')
def show_user_profile(level1):
    # show the user profile for that user
    return f'Showing level1:{level1}'


def main():
    print("hello!")
    (folders, files) =  get_folders_and_files(BASE_PATH)
    print(folders)
    print(files)

if __name__ == "__main__":
    main()    