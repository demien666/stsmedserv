from flask import Flask, render_template, url_for
from typing import Tuple, List
import os
from dataclasses import dataclass
import configparser

config = configparser.ConfigParser()
config.read("stsmedserv.ini")

URI_PATH_SEP = "->"
URI_SPACE = "%20"
PATH_SEP = "/"
BASE_PATH = config["main"]["base_path"]
ROOT_FOLDER_FILTER = config["main"].get("root_folder_filter", None)
VID_EXT = [".avi", ".mkv", ".mp4", ".m4v"]

app = Flask(__name__, static_folder=BASE_PATH)


@dataclass
class FileInfo:
    uri: str
    name: str
    real_path: str = ""

    def __lt__(self, other):
        return self.name < other.name


GLOBAL_FILES: List[FileInfo] = []


def uri_to_path(uri: str) -> str:
    return uri.replace(URI_PATH_SEP, PATH_SEP).strip().replace(URI_SPACE, " ")


def path_to_uri(path: str) -> str:
    uri = path.replace(PATH_SEP, URI_PATH_SEP).strip().replace(" ", URI_SPACE)
    if uri.startswith(URI_PATH_SEP):
        return uri[len(URI_PATH_SEP) :]
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


def upper_path(path: str) -> str:
    parts = path.split(PATH_SEP)
    if len(parts) == 1:
        return path
    head = parts[:-1]
    return PATH_SEP.join(head)


def get_folders_and_files(
    dir_path: str, folder_filter: List[str]
) -> Tuple[List[FileInfo], List[FileInfo]]:
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
            if len(folder_filter) == 0 or file_name in folder_filter:
                folders.append(file_info)
    folders.sort()
    files.sort()
    global GLOBAL_FILES
    GLOBAL_FILES = files
    return folders, files


def folders_to_groups(folders: List[str]) -> List[List[str]]:
    # print(f"getting groups for: {folders}")
    GROUP_SIZE = 5
    result = []
    group = []
    idx = 0
    for folder in folders:
        group.append(folder)
        idx = idx + 1
        if idx >= GROUP_SIZE:
            idx = 0
            result.append(group)
            group = []
    result.append(group)
    return result


@app.route("/")
def hello_world():
    folder_filter = [] if ROOT_FOLDER_FILTER is None else ROOT_FOLDER_FILTER.split(",")
    return folder("", folder_filter)


@app.route("/play/<uri>")
def play(uri):
    path = uri_to_path(uri)
    # print(f"URI: {uri}" )
    # print(f"Path: {path}")
    folder = upper_path(path)
    folder_uri = path_to_uri(folder)
    # print(f"Folder: {folder}, folder_uri={folder_uri}")

    files = GLOBAL_FILES
    index = 0
    i = 0
    for f in files:
        f.real_path = uri_to_path(f.uri.replace("../play/", ""))
        f.uri = url_for("static", filename=f.real_path)
        # print(f"{path} VS {f.real_path}")
        if path in f.real_path:
            index = i
        i = i + 1
    # print(f"Index: {index}")

    return render_template(
        "video.html", video_path=path, files=files, index=index, folder_uri=folder_uri
    )


@app.route("/folder/<uri>")
def folder(uri="", folder_filter=[]):
    path = uri_to_path(uri)
    back_path = upper_path(path)
    back_uri = None if len(uri) == 0 else path_to_uri(back_path)
    # print(f"back_uri={back_uri}")
    os_path = os.path.join(BASE_PATH, path)
    (folders, files) = get_folders_and_files(os_path, folder_filter)
    groups = folders_to_groups(folders)
    # print(f"groups: {groups}")
    return render_template(
        "folder.html", groups=groups, files=files, path=path, back_uri=back_uri
    )


def main():
    print("hello!")
    folder("Downloads->Test->Dragon")
    play(
        "Downloads->Test->Dragon->Jedcy%20smokw%20Dziewi%20wiatw%20S02E03pl%20-%20CDA.mp4"
    )


if __name__ == "__main__":
    main()
