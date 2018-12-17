#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, pathlib
from setting import TEMP_PATH, LOGS_NAME


# define paths
my_path = pathlib.Path(os.path.dirname(__file__))
parent_path = pathlib.Path(os.path.dirname(my_path))
temp_path = my_path.joinpath(TEMP_PATH.strip())
# define logfile
logfile = str(parent_path.joinpath(LOGS_NAME.strip()))
# define user request time file prefix
time_file_pre = 'user_time_'


# create folder func
def mkdir(path):
    exists = os.path.exists(path)
    if exists:
        return False
    else:
        os.makedirs(path)
        return True


# search files under path
def path_files(path):
    path = pathlib.Path(path)
    file_list = []
    # os.listdir will list all folder/files under path
    for i in os.listdir(path):
        if os.path.isfile(path.joinpath(i)):
            file_list.append(i)
    return file_list


def run():
    # create temp folder
    try:
        mkdir(temp_path)
    except Exception as Err:
        raise "Crate folder Error: %s" % Err
