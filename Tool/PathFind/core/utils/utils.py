import csv
import json
import os
import re
import subprocess
import sys

import networkx as nx
from requests.exceptions import Timeout
import requests
import tarfile
import urllib
import zipfile
from queue import Queue
from ..utils.common import proxies

output_errors = False

if not output_errors:
    import warnings

    # 禁用所有告警
    warnings.filterwarnings("ignore")

# PYTHON_PATH = '/home/wyj/miniconda3/envs/p310/bin/python3'
# PYTHON_PATH = '/home/gf/wyj/miniconda3/envs/312/bin/python3'
# def find_software_list(comlist):
#     command_str = ''
#     for software_name, software_version in comlist:
#         command_str = command_str + ' ' + software_name + '==' + software_version + ' '
#     platform = '--platform Windows --platform Linux --platform Unix --platform Mac OS-X'
#     command = f'{PYTHON_PATH} -m pip  install {command_str}  --ignore-requires-python --no-compile --dry-run --ignore-installed --force-reinstall --no-warn-conflicts '
#
#     try:
#         result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
#                                 text=True)
#         output = result.stdout
#     except subprocess.CalledProcessError as e:
#         # 如果命令运行出错，则捕获异常，并输出错误信息
#         if output_errors:
#             print(command)
#             error_output = e.stderr
#             print("Error Output:", error_output)
#         return []
#     # print(output)
#
#     software_name_re = re.compile(r'Collecting\s+([\w-]+)[\s<=>(]?')
#     name_match = re.findall(software_name_re, output)
#
#     software_name_version_re = re.compile(r'(?<=Would install)(?:\s+[\w\.-]+)+')
#     name_version_match = re.search(software_name_version_re, output)
#
#     if name_version_match:
#         name_version_str = name_version_match.group(0)
#         name_version_str = name_version_str.strip()
#     else:
#         return []
#     res_list = []
#     for name_version in name_version_str.split(' '):
#         name, version = name_version.rsplit('-', 1)
#         if name in name_match:
#             res_list.append((name, version))
#     return res_list


com_re = re.compile('href="\/Pypi\/(.*?)\/(.*?)">')


def get_deponents_list_from_libraries(software_name, software_version):
    try:
        'https://libraries.io/pypi/s2c/0.0.4/dependencies'
        uilstr = f'https://libraries.io/pypi/{software_name}/{software_version}/tree'
        page_text = requests.get(uilstr)
        com_ver_list = com_re.findall(page_text.text)

    except:
        return []
    return com_ver_list


def get_deponents_list_from_open_sources_insights(software_name, software_version):
    com_ver_list = []
    try:
        'https://deps.dev/_/s/pypi/p/requests/v/2.32.3/dependencies'
        uilstr = f'https://deps.dev/_/s/pypi/p/{software_name}/v/{software_version}/dependencies'
        page_text = requests.get(uilstr)
        com_dict = json.loads(page_text.text)
        if 'dependencies' not in com_dict:
            return []
        for dep in com_dict['dependencies']:
            if 'package' not in dep or 'version' not in dep or 'name' not in dep['package']:
                continue

            com_name = dep['package']['name']
            com_version = dep['version']
            com_ver_list.append((com_name, com_version))

    except:
        return com_ver_list
    return com_ver_list


def find_software_list(comlist):
    com_ver_dict = {}
    com_ver_lists = []

    for software_name, software_version in comlist:
        com_ver_dict[software_name] = software_version
        new_com_ver_list = get_deponents_list_from_open_sources_insights(software_name, software_version)
        com_ver_lists.extend(new_com_ver_list)

    print(com_ver_lists)
    for software_name, software_version in com_ver_lists:
        if software_name == None or software_name == '' or software_name in com_ver_dict:
            continue
        com_ver_dict[software_name] = software_version

    com_ver_lists = []
    for software_name in com_ver_dict:
        com_ver_lists.append((software_name, com_ver_dict[software_name]))
    return com_ver_lists


def find_files(folder_list, file_name_suffix):
    search_files = set()
    for folder in folder_list:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(file_name_suffix):
                    file_path = os.path.join(root, file)
                    search_files.add(file_path)
    return list(search_files)


def find_all_files_in_folder(folder):
    search_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            search_files.append(file_path)
    return search_files


def get_with_retry(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5, proxies=proxies)
            return response.text  # 如果成功获取到响应，则直接返回
        except Timeout:
            print(f"Timeout occurred, retrying... (attempt {i + 1}/{max_retries})")
    return None  # 如果尝试了指定次数仍未成功，则返回 None


# res = find_software_list([('pavlok','0.1.1'),('starlette','0.14.2')])
# print(res)

def extract_tar_gz_files(file_path, folder_path):
    file_name, file_extension = os.path.splitext(file_path)
    if file_extension == '.zip':
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                target_path = os.path.join(folder_path, file)
                if os.path.exists(target_path):
                    continue
                zip_ref.extract(file, folder_path)
    elif file_extension == '.bz2':
        tf = tarfile.open(file_path)
        tf.extractall(folder_path)
    else:
        with tarfile.open(file_path, 'r:gz') as tar_ref:
            for member in tar_ref.getmembers():
                target_path = os.path.join(folder_path, member.name)
                if os.path.exists(target_path):
                    continue
                tar_ref.extract(member, folder_path)


def bfs_search_folder(root_folder, target_folder_name):
    q = Queue()
    q.put(root_folder)
    matches = []  # 保存匹配到的子文件夹路径

    while not q.empty():
        current_folder = q.get()
        if not os.path.isdir(current_folder):
            continue
        for item in os.listdir(current_folder):
            item_path = os.path.join(current_folder, item)
            if os.path.isdir(item_path):
                if item == target_folder_name:
                    matches.append(item_path)  # 将匹配到的子文件夹路径添加到列表
                else:
                    q.put(item_path)

    return matches  # 返回匹配到的所有子文件夹路径


def find_file_in_folder(folder_path, target_file):
    for root, dirs, files in os.walk(folder_path):
        if target_file in files:
            return os.path.join(root, target_file)

    return None


def read_json_file(json_file_name):
    with open(json_file_name, 'r') as json_file_name_f:
        return json.load(json_file_name_f)


def write_json_file(json_file_name, json_dict):
    with open(json_file_name, 'w') as json_file_name_f:
        json.dump(json_dict, json_file_name_f, indent=4)


def judgepath(gragh, source_point_list, sink_point_list):
    all_nodes = set()
    edges = []
    # 创建有向图对象
    G = nx.DiGraph()
    # 构建邻接表
    for node, neighbors in gragh.items():
        all_nodes.add(node)
        if not neighbors:
            continue
        for neighbor in neighbors:
            edges.append((node, neighbor))
        all_nodes.update(neighbors)

    G.add_edges_from(edges)
    isolated_nodes = all_nodes - set(G.nodes())
    G.add_nodes_from(isolated_nodes)
    # 检查并删除不在邻接表中的起始点和汇聚点
    _source_point_list = [node for node in source_point_list if node in all_nodes]
    _sink_point_list = [node for node in sink_point_list if node in all_nodes]
    # 判断起始点到汇聚点的所有调用路径
    all_paths = []
    # 如果源点和汇点是同一个点，把当前函数加入调用路径
    all_paths.extend([[point] for point in set(_source_point_list) & set(_sink_point_list)])
    print('start', _source_point_list)
    print('sink', _sink_point_list)
    for _source_point in _source_point_list:
        for _sink_point in _sink_point_list:
            path = list(nx.all_simple_paths(G, source=_source_point, target=_sink_point,cutoff=10))
            # path = list(nx.shortest_simple_paths(G, source=_source_point, target=_sink_point))
            if path:
                all_paths.extend(path)
            # try:
            #     path = nx.shortest_path(G, source=_source_point, target=_sink_point)
            #     if path:
            #         all_paths.append(list(path))
            # except Exception as e:
            #     continue


    return all_paths

csv.field_size_limit(10**7)
def parse_csv_file(file_path, skip_frist_row=False):
    with open(file_path, "r", newline="") as file:
        reader = csv.reader(file)
        if skip_frist_row:
            next(reader)
        data = [row for i, row in enumerate(reader) if i > 0]
    return data
