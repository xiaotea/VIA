import ast
import csv
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import sys
import networkx as nx
from setuptools import find_packages

from pathlib import Path

# 获取当前执行文件的绝对路径
current_file = Path(__file__).resolve()  # __file__ 是当前文件路径

# 父目录
parent_dir = current_file.parent
mapping_file_path = os.path.join(parent_dir,"machinery")


current_directory = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, current_directory)

from processing.codeFilePreprocessing import other_py_file_deal
from tool.Jarvis.external_interface import jarvis_callgraph_gen


def save_call_graph(software_abs_dir, call_graph):
    # print(call_graph)
    if call_graph == None:
        return
    with open(os.path.join(software_abs_dir, 'call_graph'), 'w', encoding='utf-8') as call_graph_file:
        call_graph_file.write(json.dumps(call_graph))


def find_file_in_folder(folder_path, target_file):
    for root, dirs, files in os.walk(folder_path):
        if target_file in files:
            return os.path.join(root, target_file)

    return None


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


def get_lib_file_name_map():
    lib_map = dict()
    mapping_abs_file_path = os.path.join(mapping_file_path, 'mapping')
    with open(mapping_abs_file_path, 'r') as f:
        lib_map_str = f.read()
        lib_map_list = lib_map_str.strip().split('\n')
        for lib_name_str in lib_map_list:
            lib_map[lib_name_str.split(':')[1]] = lib_name_str.split(':')[0]
    return lib_map


LIB_MAP = get_lib_file_name_map()


def find_deploy_dir(software_abs_dir, software_name):
    def extract_packages_variable_from_setup_file(file_path):
        # 解析setup文件中的变量
        packages = []
        with open(file_path, "r", encoding='utf-8') as file:
            content = file.read()
        try:
            tree = ast.parse(content)
        except:
            return packages
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "setup":
                for keyword in node.keywords:
                    # todo :解析配置文件中的部署位置
                    # setup_variables = toml.load("pyproject.toml")["tool"]["flit"]["metadata"]
                    # packages=[setup_variables["module"]]
                    #
                    try:
                        if keyword.arg == "packages" and isinstance(keyword.value, ast.List):
                            packages = [elt.s for elt in keyword.value.elts]
                            break
                    except Exception as e:
                        pass
        return packages

    def find_deploy_packages_with_setupfile(file_path):
        # 寻找setup文件
        packages_list = []
        setup_file_path = find_file_in_folder(file_path, 'setup.py')
        if not setup_file_path:
            return packages_list
        with open(setup_file_path, 'r', encoding='utf-8') as setup_file:
            if 'find_packages' in setup_file.read():
                file_path = os.path.dirname(setup_file_path)
                if os.path.exists(os.path.join(file_path, 'src')):
                    file_path = os.path.join(file_path, 'src')
                pre_packages_list = find_packages(file_path, exclude=('examples', 'docs', 'tests', 'tests.*'))

                if not pre_packages_list:
                    return packages_list
                for package in pre_packages_list:
                    if package.split('.')[0] not in packages_list:
                        packages_list.append(package.split('.')[0])
            else:
                pre_packages_list = extract_packages_variable_from_setup_file(setup_file_path)
                for package in pre_packages_list:
                    if package.split('.')[0] not in packages_list:
                        packages_list.append(package.split('.')[0])

        res_packages_list = []
        for lib_folder in packages_list:
            if lib_folder == 'tests':
                continue
            res_packages_list.append(lib_folder)

        return res_packages_list

    def find_deploy_packages_with_toplevelfile(file_path):
        # 寻找top_level.txt 并解析
        packages_list = []
        top_level_file_path = find_file_in_folder(file_path, 'top_level.txt')
        if top_level_file_path:
            with open(top_level_file_path, 'r', encoding='utf-8') as top_level_file_hander:
                lib_folder_list = top_level_file_hander.read().strip().split('\n')
            for lib_folder in lib_folder_list:
                if lib_folder == 'tests' or lib_folder.startswith('tests.'):
                    continue
                packages_list.append(lib_folder)

        return packages_list

    def find_deploy_lib_list(file_path, lib_name):
        # 根据toplevel找部署的包名
        lib_folder_list = find_deploy_packages_with_toplevelfile(file_path)
        if not lib_folder_list:
            lib_folder_list = find_deploy_packages_with_setupfile(file_path)
        if not lib_folder_list:
            lib_folder = lib_name
            if lib_name in LIB_MAP:
                lib_folder = LIB_MAP[lib_name]
            lib_folder_list = [lib_folder]

        return lib_folder_list

    def find_deploy_path_list(deploy_lib_list, file_path):
        if not deploy_lib_list:
            return [file_path]
        deploy_path_list = []
        for deploy_lib_name in deploy_lib_list:
            file_path_list = bfs_search_folder(file_path, deploy_lib_name)
            if file_path_list:
                deploy_path_list.append(file_path_list[0])

        return deploy_path_list

    deploy_dir_list = []
    deploy_dir_abs_list = []

    if software_abs_dir:
        deploy_dir_list = find_deploy_lib_list(software_abs_dir, software_name)

    if deploy_dir_list:
        for deploy_dir in deploy_dir_list:
            LIB_MAP[deploy_dir] = software_name
        deploy_dir_abs_list = find_deploy_path_list(deploy_dir_list, software_abs_dir)

        if not deploy_dir_abs_list:
            deploy_dir_abs_list = [str(software_abs_dir)]
    return deploy_dir_abs_list


def find_files(folder_list, file_name_suffix):
    search_files = []
    for folder in folder_list:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(file_name_suffix):
                    file_path = os.path.join(root, file)
                    search_files.append(file_path)
    return list(set(search_files))


def get_total_file_size(file_list):
    """
    计算；根据列表中所有文件大小计算max_iter大小
    """
    total_size = 0
    for file_path in file_list:
        if os.path.isfile(file_path):
            total_size += os.path.getsize(file_path)
        else:
            print(f"Warning: {file_path} is not a valid file or does not exist.")

    total_size_mb = total_size / (1024 * 1024)  # Convert size to MB

    if total_size_mb < 1:
        return -1
    elif 1 <= total_size_mb <= 5:
        return 3
    else:
        return 1


def write_file(file_path, content):
    with open(file_path, 'w') as f:
        f.write(content)


def analyze_call_graph(software_abs_dir, deploy_file_list):
    if not software_abs_dir:
        return
    call_graph = jarvis_callgraph_gen(deploy_file_list, package=software_abs_dir)
    save_call_graph(software_abs_dir, call_graph)


def gen_callgraph(base_dir, dir_name):
    software_dir = os.path.join(base_dir, dir_name)
    print(software_dir)
    software_abs_dir = os.path.abspath(software_dir)

    if "@" not in dir_name:
        return
    com_name = dir_name.split('@')[0]
    com_version = dir_name.split('@')[1]
    if 'call_graph' in os.listdir(software_abs_dir):
        print(dir_name, '已经分析过')
        return
    deploy_dir_abs_list = find_deploy_dir(software_abs_dir, com_name)

    uncompyle_files = find_files(deploy_dir_abs_list, ('.pyc', '.pyx', '.pyi', '.pyw'))
    write_file(os.path.join(software_abs_dir, 'uncompyle_files'), json.dumps(uncompyle_files, indent=4))
    for predeal_file in uncompyle_files:
        other_py_file_deal(predeal_file)

    all_files_list = find_files([software_abs_dir], '.py')
    write_file(os.path.join(software_abs_dir, 'all_files'), json.dumps(all_files_list, indent=4))

    deploy_files_list = find_files(deploy_dir_abs_list, '.py')
    write_file(os.path.join(software_abs_dir, 'deploy_files'), json.dumps(deploy_files_list, indent=4))
    print(dir_name)

    analyze_call_graph(software_abs_dir, deploy_files_list)


    return None


def split_list(lst, i, n):
    """
    将列表分成n份的函数,取第i份
    """
    if not lst or n < 1 or i < 1 or i > n:
        return []

    length = len(lst)
    size = length // n
    remainder = length % n

    start = (i - 1) * size + min(i - 1, remainder)
    end = start + size + (1 if i <= remainder else 0)

    return lst[start:end]


def read_csv_file(csv_file):
    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = [row for row in reader]  # 读取剩余所有行数据
        return data
    except Exception as e:
        print(f"Error reading CSV file {csv_file}")
        return None


def add_have_analyze(com_str, filepath):
    with open(filepath, mode='a', encoding='utf-8') as file:
        file.write(com_str + '\n')


def write_log(file_num, message):
    with open('log/log' + str(file_num), 'a+', encoding='utf-8') as f:
        f.write(str(message) + '\n')


