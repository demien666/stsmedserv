from flask import Flask, render_template, url_for
from typing import Tuple, List
import os
from dataclasses import dataclass
import configparser

config = configparser.ConfigParser()
config.read('stsmedserv.ini')

URI_PATH_SEP = "->"
URI_SPACE = "___"
PATH_SEP = "/"
BASE_PATH = config["main"]["base_path"]
VID_EXT = [".avi", ".mkv", ".mp4"]

app = Flask(__name__, static_folder=BASE_PATH)

@dataclass
class FileInfo:
    uri: str
    name: str
    real_path: str = ""

    def __lt__(self, other):
        return self.name < other.name

def uri_to_path(uri: str) -> str:
    return uri.replace(URI_PATH_SEP, PATH_SEP).strip().replace(URI_SPACE, " ")

def path_to_uri(path: str) -> str:
    uri = path.replace(PATH_SEP, URI_PATH_SEP).strip().replace(" ", URI_SPACE)
    if uri.startswith(URI_PATH_SEP):
        return uri[len(URI_PATH_SEP):]
    else:
        return uri    

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
        local_path = full_path.replace(BASE_PATH, "")
        uri = "../play/" + path_to_uri(local_path)
        file_info = FileInfo(uri, remove_file_extension(file_name), local_path)
        if os.path.isfile(full_path):
            if is_video_file(file_name):
                files.append(file_info)
        else:
            file_info.uri = "../folder/" + path_to_uri(local_path)
            folders.append(file_info)
    folders.sort()
    files.sort()        
    return folders, files         

@app.route("/")
def hello_world():
    return folder()

@app.route("/play/<uri>")
def play(uri):
    path = uri_to_path(uri)
    #print(path)
    return render_template('video.html', video_path=path)

@app.route("/folder/<uri>")
def folder(uri=""):
    path = uri_to_path(uri)
    full_path = os.path.join(BASE_PATH, path)
    (folders, files) =  get_folders_and_files(full_path)
    return render_template('folder.html', folders=folders, files=files, path=path)    


def main():
    print("hello!")
    

if __name__ == "__main__":
    main()    