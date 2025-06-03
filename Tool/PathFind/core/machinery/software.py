import ast
import json
import os
import urllib
from setuptools import find_packages
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..tool.Py2ToPy3.py2to3 import change_pyfile_list_2_to_3
from ..utils import get_with_retry, extract_tar_gz_files, find_file_in_folder, bfs_search_folder, find_files, \
    read_json_file, write_json_file
from ..utils.common import LIB_MAP, DATA_DIR
from ..utils.utils import output_errors
from .importAnalyze import get_used_pckages
from ..processing.codeFilePreprocessing import other_py_file_deal
from ..tool.Jarvis.external_interface import jarvis_callgraph_gen
from ..utils.common import proxies

proxy_handler = urllib.request.ProxyHandler(proxies)
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

class SoftwareManager:

    def __init__(self, software_name, software_version):
        self.software_name = software_name
        self.software_version = software_version
        self.have_source_code = False
        self.software_abs_dir = None

        # 软件部署的包列表
        self.deploy_dir_list = []
        self.deploy_dir_abs_list = []

        self.call_graph = None

        # 软件部署的文件列表
        self.deploy_file_list = []
        # 软件所有文件列表
        self.all_file_list = []
        self.is_vul_software = False
        self.is_main_software = False

        # 软件所有使用的包列表
        self.all_used_package_list = []
        # 软件部署的包使用的包列表
        self.deploy_used_package_list = []
        self.setUp()

    def analyze_used_package_list(self):
        # 分析使用的包列表
        if self.have_source_code == False:
            self.deploy_used_package_list = []
            self.all_used_package_list = []
            return
        if self.software_abs_dir:
            deploy_file_list_path = find_file_in_folder(self.software_abs_dir, 'deploy_file_used_list')
            if deploy_file_list_path:
                try:
                    self.deploy_used_package_list = read_json_file(deploy_file_list_path)
                except:
                    pass

            all_file_list_path = find_file_in_folder(self.software_abs_dir, 'all_file_used_list')
            if all_file_list_path:
                try:
                    self.all_used_package_list = read_json_file(all_file_list_path)
                except Exception as e:
                    pass
        if not self.deploy_used_package_list:
            self.deploy_used_package_list = get_used_pckages(self.deploy_file_list)
            write_json_file(os.path.join(self.software_abs_dir, 'deploy_file_used_list'), self.deploy_used_package_list)
        if not self.all_used_package_list:
            self.all_used_package_list = get_used_pckages(self.all_file_list)
            write_json_file(os.path.join(self.software_abs_dir, 'all_file_used_list'), self.all_used_package_list)

    def find_deploy_file(self):
        # 加py文件反编译
        predeal_files = find_files(self.deploy_dir_abs_list, ('.pyc', '.pyx', '.pyi', '.pyw'))
        for predeal_file in predeal_files:
            other_py_file_deal(predeal_file)

        self.deploy_file_list = find_files(self.deploy_dir_abs_list, '.py')
        change_pyfile_list_2_to_3(self.deploy_file_list)

    def find_software_all_file(self):
        if not self.software_abs_dir:
            self.all_file_list = []
            return
        self.all_file_list = find_files([self.software_abs_dir], '.py')

    def have_call_graph_file(self):
        if not self.software_abs_dir:
            return False

        if find_file_in_folder(self.software_abs_dir, 'call_graph'):
            return True
        return False

    def load_call_graph(self):
        with open(os.path.join(self.software_abs_dir, 'call_graph'), 'r', encoding='utf-8') as call_graph_file:
            return json.loads(call_graph_file.read())

    def load_diff_version_callgraph(self):
        callgraph_components_set = set()
        all_component_list = os.listdir(DATA_DIR)
        for component_version in all_component_list:
            if not os.path.isdir(os.path.join(DATA_DIR, component_version)):
                continue
            if component_version.split('@')[0].lower() != self.software_name.lower():
                continue

            if find_file_in_folder(os.path.join(DATA_DIR, component_version), 'call_graph'):
                with open(os.path.join(DATA_DIR, component_version, 'call_graph'), 'r',
                          encoding='utf-8') as call_graph_file:
                    self.call_graph = json.loads(call_graph_file.read())
                    return True

        return False

    def save_call_graph(self):
        if self.call_graph == None:
            return
        with open(os.path.join(self.software_abs_dir, 'call_graph'), 'w', encoding='utf-8') as call_graph_file:
            call_graph_file.write(json.dumps(self.call_graph))

    def analyze_call_graph(self):
        if self.have_call_graph_file():
            self.call_graph = self.load_call_graph()

        elif not self.is_vul_software and self.is_main_software and self.load_diff_version_callgraph():
            pass
        else:
            self.call_graph = jarvis_callgraph_gen(self.deploy_file_list, package=self.software_abs_dir)
            self.save_call_graph()
        return self.call_graph

    def get_call_graph(self):
        if self.call_graph:
            return self.call_graph
        else:
            return {}

    def setUp(self):
        if self.download_source_code():
            self.have_source_code = True
        else:
            self.have_source_code = False
            return
        self.find_deploy_dir()
        self.find_deploy_file()
        self.find_software_all_file()

    def find_deploy_dir(self):
        def extract_packages_variable_from_setup_file(file_path):
            packages = []
            with open(file_path, "r", encoding='utf-8') as file:
                content = file.read()
            try:
                tree = ast.parse(content)
            except:
                return packages
            try:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "setup":
                        for keyword in node.keywords:
                            if keyword.arg == "packages" and isinstance(keyword.value, ast.List):
                                packages = [elt.s for elt in keyword.value.elts]
                                if packages:
                                    return packages
                variable_values = {}
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):  # 处理赋值语句
                        for target in node.targets:
                            if isinstance(target, ast.Name):  # 确保是变量赋值
                                if isinstance(node.value, ast.List):  # 变量是列表
                                    variable_values[target.id] = [elt.s for elt in node.value.elts if
                                                                  isinstance(elt, ast.Str)]
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "setup":
                        for keyword in node.keywords:
                            if keyword.arg == "packages":
                                if isinstance(keyword.value, ast.List):  # 直接传递列表
                                    packages = [elt.s for elt in keyword.value.elts if isinstance(elt, ast.Str)]
                                elif isinstance(keyword.value, ast.Name):  # 传递的是变量
                                    packages = variable_values.get(keyword.value.id, [])
            except Exception as e:
                print(e)

            return packages

        def find_deploy_packages_with_setupfile(file_path):
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
                lib_folder_list = [lib_folder.replace("-","_")]

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

        if self.have_source_code == False:
            self.deploy_dir_list = []
            self.deploy_dir_abs_list = []

        if self.software_abs_dir:
            self.deploy_dir_list = find_deploy_lib_list(self.software_abs_dir, self.software_name)

        if self.deploy_dir_list:
            for deploy_dir in self.deploy_dir_list:
                LIB_MAP[deploy_dir] = self.software_name
            self.deploy_dir_abs_list = find_deploy_path_list(self.deploy_dir_list, self.software_abs_dir)

            if not self.deploy_dir_abs_list:
                self.deploy_dir_abs_list = [str(self.software_abs_dir)]

    def download_source_code(self):
        def find_source_url(pypi_page_json):
            try:
                source_dict = json.loads(pypi_page_json)
            except Exception as json_error:
                print(json_error)
                return ''
            if source_dict.get('message', '') == 'Not Found' or 'urls' not in source_dict:
                return ''
            source_url = ''
            for url_dict in source_dict['urls']:
                if 'python_version' not in url_dict or 'url' not in url_dict:
                    continue
                if url_dict['python_version'] == 'source':
                    source_url = url_dict['url']
                    break
            return source_url

        def download_file(url, save_directory, num_retries=3):
            file_name = os.path.basename(url)
            file_path = os.path.join(save_directory, file_name)

            if os.path.exists(file_path):
                if output_errors:
                    print(f"File already exists: {file_path}")
                return file_name
            for _ in range(num_retries):
                try:

                    with urllib.request.urlopen(url, timeout=10) as response, open(file_path, 'wb') as out_file:
                        out_file.write(response.read())
                    print(f"File downloaded successfully and saved at: {file_path}")
                    return file_name
                except urllib.error.URLError as e:
                    print("Failed to download the file:", e)
                except IOError as e:
                    print("Failed to save the file:", e)
                except Exception as e:
                    print("Failed to download the file:", e)
            print(f"Failed to deal the file after {num_retries} attempts")
            return None

        def download_install_file(software_name, software_version):
            # 存储tar.gz文件的位置  DATA_DIR
            software_file_path = software_name + '@' + software_version
            software_file_path = os.path.join(DATA_DIR, software_file_path)
            if not os.path.exists(software_file_path):
                os.makedirs(software_file_path)
            com_pypi_url = f'https://pypi.org/pypi/{software_name}/{software_version}/json'
            com_pypi_page = get_with_retry(com_pypi_url)
            if not com_pypi_page:
                print("组件链接爬取失败")
                return None
            href = find_source_url(com_pypi_page)
            if href == '':
                print(com_pypi_url)
                print('该组件没有源码')
                return None

            if download_file(href, software_file_path):
                file_name = os.path.basename(href)
                file_path = os.path.join(software_file_path, file_name)
                try:
                    extract_tar_gz_files(file_path, software_file_path)
                except:
                    os.remove(file_path)
                    return None
            return software_file_path

        if not self.software_name or not self.software_version:
            return None
        if self.software_name + "@" + self.software_version in os.listdir(DATA_DIR):
            self.software_abs_dir = os.path.join(DATA_DIR, self.software_name + "@" + self.software_version)
            return self.software_abs_dir
        software_file_path = download_install_file(self.software_name, self.software_version)
        if software_file_path:
            self.software_abs_dir = software_file_path
            return software_file_path
        else:
            return None



