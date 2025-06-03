import os

current_folder_path = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(current_folder_path)
from pathlib import Path
# 获取当前执行文件的绝对路径
current_file = Path(__file__).resolve()  # __file__ 是当前文件路径
# 父目录
parent_dir = current_file.parent.parent.parent
DATA_DIR = os.path.join(parent_dir,r'data')
# DATA_DIR = r"F:\python_project\data"
local_software_version_dict = {}
_local_software_version_list = os.listdir(DATA_DIR)
for _local_software_version in _local_software_version_list:
    _local_software_name = _local_software_version.split('@')[0]
    _local_software_version = _local_software_version.split('@')[1]
    if _local_software_name not in local_software_version_dict:
        local_software_version_dict[_local_software_name] = []
    if _local_software_version not in local_software_version_dict[_local_software_name]:
        local_software_version_dict[_local_software_name].append(_local_software_version)

proxies = {
    'http':'http://127.0.0.1:10809',
    'https':'http://127.0.0.1:10809'
}


def find_close_version(s_version, s_version_list):
    if not s_version or not s_version_list:
        return None
    # Find the longest common prefix
    s_lenth = len(s_version)

    for i in range(s_lenth, 0, -1):
        char = s_version[:i]
        for s in s_version_list:
            if len(s) > i:
                continue
            if s.startswith(char):
                return s
    return None


def get_local_software_version(grep_software_name:str, grep_software_version:str):
    if grep_software_name not in local_software_version_dict:
        return None
    if grep_software_version not in local_software_version_dict[grep_software_name]:
        return find_close_version(grep_software_version, local_software_version_dict[grep_software_name])
    else:
        return grep_software_version

def get_lib_file_name_map():
    lib_map = dict()
    mapping_abs_file_path = os.path.join(parent_folder, 'machinery', 'mapping')
    with open(mapping_abs_file_path, 'r') as f:
        lib_map_str = f.read()
        lib_map_list = lib_map_str.strip().split('\n')
        for lib_name_str in lib_map_list:
            lib_map[lib_name_str.split(':')[1]] = lib_name_str.split(':')[0]
    return lib_map


LIB_MAP = get_lib_file_name_map()
