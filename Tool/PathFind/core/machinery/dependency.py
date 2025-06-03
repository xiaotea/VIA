from .pathAnalyze import PathManager
from ..utils import judgepath


class DependencyManager:
    def __init__(self, software_list, vul_software_name, main_software_name, vul_fun_list):
        self.vul_software_name = vul_software_name
        self.main_software_name = main_software_name
        self.vul_fun_list = vul_fun_list
        print(self.vul_fun_list)

        self.software_list = software_list

        # 软件名和软件对象之间的索引
        self.software_map = {}

        # 软件和软件之间的依赖关系
        self.deploy_dependency = {}
        self.dependency_init()

        # 待检测软件到漏洞软件的调用路径
        self.all_dependency = {}

        # 依赖路径
        self.dependency_path = []
        # 依赖路径map
        self.dependency_path_map = {}

        # 包对应的模块 集合
        self.pkg_mapping = {}

        self.dependency_call_point_map = {}

        self.setUp()

    def dependency_init(self):
        if not self.software_list:
            return
        for software in self.software_list:
            self.deploy_dependency[software.software_name] = []

    def get_software_obj(self, software_name):
        return self.software_map[software_name]

    def add_deploy_dependency(self, used_pkg_dir, software_name):
        if not used_pkg_dir in self.pkg_mapping:
            return

        if not software_name in self.deploy_dependency:
            self.deploy_dependency[software_name] = []
        for _used_software in  self.pkg_mapping[used_pkg_dir]:
            if _used_software in self.deploy_dependency[software_name]:
                return
            if _used_software == software_name:
                return
            self.deploy_dependency[software_name].append(_used_software)

    def add_all_dependency(self, used_pkg_dir, software_name):
        if not used_pkg_dir in self.pkg_mapping:
            return
        if not software_name in self.all_dependency:
            self.all_dependency[software_name] = []
        for _used_software in self.pkg_mapping[used_pkg_dir]:
            if _used_software in self.all_dependency[software_name]:
                return
            if _used_software == software_name:
                return
            self.all_dependency[software_name].append(_used_software)

    def setUp(self):
        # 建立组件和对象的对应关系
        for software_obj in self.software_list:
            self.software_map[software_obj.software_name] = software_obj

        # 标记漏洞组件

        vul_software = self.get_software_obj(self.vul_software_name)
        vul_software.is_vul_software = True

        _main_software_name = self.get_software_obj(self.main_software_name)
        _main_software_name.is_main_software = True

        # 建立部署包名和组件名对应关系图
        for software_obj in self.software_list:
            for deploy_dir in software_obj.deploy_dir_list:
                if deploy_dir not in self.pkg_mapping:
                    self.pkg_mapping[deploy_dir] = []
                if software_obj.software_name not in self.pkg_mapping[deploy_dir]:
                    self.pkg_mapping[deploy_dir].append(software_obj.software_name)

        # 建立软件之间的依赖关系图
        for software_obj in self.software_list:

            for used_pkg_dir in software_obj.deploy_used_package_list:
                self.add_deploy_dependency(used_pkg_dir, software_obj.software_name)

            for used_pkg_dir in software_obj.all_used_package_list:
                self.add_all_dependency(used_pkg_dir, software_obj.software_name)


    def get_deploy_dependency_map(self):
        if self.deploy_dependency:
            return self.deploy_dependency

    def get_all_dependency_map(self):
        if self.all_dependency:
            return self.all_dependency

    def find_dependency_path(self):
        if self.deploy_dependency:
            self.dependency_path = judgepath(
                self.deploy_dependency,
                [self.main_software_name],
                [self.vul_software_name])
        return self.dependency_path

    def analyze_fun_path(self):

        def save_path_info(index, up_software, down_software, path_obj):
            self.dependency_path_map[str(index)][up_software + '#' + down_software] = path_obj.get_info()

        # 初始化细粒度分析
        if self.dependency_path:
            for index, path in enumerate(self.dependency_path):
                # 取出每个可达路径
                self.dependency_path_map[str(index)] = {}
                software_name_tem = None
                for _software_name in reversed(path):
                    if not software_name_tem:
                        software_name_tem = _software_name
                        continue
                    self.dependency_path_map[str(index)][software_name_tem + '#' + _software_name] = {}
                    software_name_tem = _software_name
        else:
            return

        for index, path in enumerate(self.dependency_path):

            print('路径：', index, path)

            # 取出每个可达路径
            software_name_tem = None
            reached_sink_list = self.vul_fun_list.copy()
            for _software_name in reversed(path):
                print('下游组件：', _software_name, '上游组件：', software_name_tem)
                if not software_name_tem:
                    software_name_tem = _software_name
                    continue

                path_obj_tem = PathManager(
                    self.get_software_obj(software_name_tem),
                    self.get_software_obj(_software_name),
                    reached_sink_list
                )

                reached_sink_list = path_obj_tem.get_reached_source_list()
                save_path_info(index, software_name_tem, _software_name, path_obj_tem)
                if not reached_sink_list:
                    print(f'{index}路径中{software_name_tem}不可达')
                    break
                software_name_tem = _software_name

    def get_fun_reachable_info(self):
        return self.dependency_path_map
