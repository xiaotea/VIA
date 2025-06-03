import json
import os
from concurrent.futures import ThreadPoolExecutor

from PathFind.core.machinery.software import SoftwareManager
from machinery.dependency import DependencyManager
from utils.utils import find_software_list
from utils.utils import parse_csv_file, find_file_in_folder

file_path = '/home/gf/wyj/python_test/PathFind/core/data_set'
def read_fail_log():
    with open(os.path.join(file_path, "fail_log"), 'a') as f:
        read_cont = f.read()
    return read_cont.strip().split('\n')
fail_list = read_fail_log()


def write_fail_log(map_name, try_times=50):
    try:
        with open(os.path.join(file_path, "fail_log"), 'a') as f:
            f.write(map_name + '\n')
    except IOError:
        if try_times > 0:
            write_fail_log(map_name, try_times=try_times - 1)

def find_dependency(up_software_name, up_software_version, down_software_name, down_software_version):
    software_list = find_software_list(
        [(up_software_name, up_software_version), (down_software_name, down_software_version)])
    software_obj_list = []
    software_version_map = {}
    res_info = {}

    for software_name, software_version in software_list:
        software_obj = SoftwareManager(software_name, software_version)
        if not software_obj.have_source_code:
            return
        software_obj_list.append(software_obj)
        software_version_map[software_name] = software_version

    # for software_obj in software_obj_list:
    #     if not software_obj.have_source_code:
    #         print(software_obj.software_name,software_obj.software_version,"没有源码")
    #         return

    for software_obj in software_obj_list:
        software_obj.analyze_used_package_list()

    # vul_fun_list = ['src/urllib3/poolmanager.PoolManager.urlopen']

    dependency_manager = DependencyManager(software_obj_list, up_software_name, down_software_name, [])
    # dependency_manager.find_dependency_path()
    # dependency_manager.analyze_fun_path()
    # print(dependency_manager.dependency_path_map)
    # print(dependency_manager.get_dependency_map())
    res_info["Versionmap"] = software_version_map
    res_info["dependency"] = dependency_manager.get_dependency_map()
    res_info["dependency_path"] = dependency_manager.find_dependency_path()

    return res_info


def process_com(com):
    up_com_name, up_com_version = com[1].split('@')
    down_com_name, down_com_version = com[2].split('@')

    map_file = f"{up_com_name}@{up_com_version}@{down_com_name}@{down_com_version}"

    if map_file in fail_list:
        return

    if find_file_in_folder(os.path.join('core', 'data_set'), map_file):
        return

    dependency_map = find_dependency(up_com_name, up_com_version, down_com_name, down_com_version)
    if dependency_map:
        with open(os.path.join('core', 'data_set', map_file), 'w') as f:
            print("分析完成", map_file)
            if map_file == {}:
                write_fail_log(map_file)
                return
            json.dump(dependency_map, f, indent=4)




def parse_and_process_csv(up_down_list):
    with ThreadPoolExecutor(max_workers=40) as executor:
        for com in up_down_list:
            executor.submit(process_com, com)


up_down_list = parse_csv_file('python_上下游组件_删减.csv')

parse_and_process_csv(up_down_list)
