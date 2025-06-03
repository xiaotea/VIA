import networkx as nx

from ..utils import judgepath


class PathManager:
    def __init__(self, up_software, down_software, sink_list):

        self.down_software = down_software
        self.up_software = up_software
        self.sink_list = sink_list
        self.source_list = []

        self.reached_source_list = []

        self.path = []
        # 用了上游的那些函数、类
        self.used_up_in_down_list = []
        # 下游的哪些函数，用了上游的调用,形成图
        self.down_list_used_up_map = {}
        self.reached_sink_list = []

        self.analyze_all_call_graph()

        self.used_fun_map = dict()
        self.analyze_source_list()
        self.analyze_path()
        self._get_reached_source_list()


    def get_info(self):
        output_info = {}
        output_info['sink_list'] = self.sink_list.copy()
        output_info['source_list'] = self.source_list.copy()
        output_info['path'] = self.path.copy()
        output_info['used_up_in_down_list'] = self.used_up_in_down_list.copy()
        output_info['reached_source_list'] = self.reached_source_list.copy()
        output_info['down_list_used_up_map'] = self.down_list_used_up_map.copy()
        output_info['reached_sink_list'] = self.reached_sink_list.copy()
        return output_info

    def get_source_list(self):
        return self.source_list

    def get_path(self):
        return self.path

    def is_reachable(self):
        if not self.path or self.sink_list or self.source_list:
            return False
        return True

    def analyze_all_call_graph(self):
        self.down_software.analyze_call_graph()
        self.up_software.analyze_call_graph()

    def analyze_source_list(self):
        def find_down_list_used_up_map(_down_callgraph, used_up_in_down_list):
            down_list_used_up_map = {}
            if not used_up_in_down_list:
                return {}
            for node, neighbors in _down_callgraph.items():
                for neighbor in neighbors:
                    if neighbor not in used_up_in_down_list:
                        continue
                    if node not in down_list_used_up_map:
                        down_list_used_up_map[node] = []
                    if neighbor not in down_list_used_up_map[node]:
                        down_list_used_up_map[node].append(neighbor)
            return down_list_used_up_map

        deploy_dir_list = self.up_software.deploy_dir_list.copy()
        down_callgraph = self.down_software.call_graph
        up_callgraph = self.up_software.call_graph

        #   找出使用了哪些函数或者类或者文件
        self.used_up_in_down_list = extract_keys_with_prefix(down_callgraph, deploy_dir_list)

        self.down_list_used_up_map = find_down_list_used_up_map(down_callgraph, self.used_up_in_down_list)

        # 关联出更详细的函数或者类
        self.source_list, self.used_fun_map = find_used_node_in_call_gragh(up_callgraph, self.used_up_in_down_list.copy())
        self.source_list = list(set(self.source_list))

    def get_reached_source_list(self):
        return self.reached_sink_list

    def analyze_path(self, sink_point_list=None):
        if sink_point_list:
            self.sink_list = sink_point_list

        if self.up_software.is_vul_software:
            print(f"原始漏洞函数，", self.sink_list)
            self.sink_list, _ = find_used_node_in_call_gragh(self.up_software.call_graph, self.sink_list)
            self.sink_list = list(set(self.sink_list))
            print(f"匹配后漏洞函数，", self.sink_list)

        self.path = judgepath(self.up_software.call_graph, self.source_list, self.sink_list)

    def _get_reached_source_list(self):
        if not self.path:
            self.reached_source_list = []
            return []
        #
        # 在上游中有路径的source点
        reached_source_set = set()
        for every_path in self.path:
            reached_source_set.add(every_path[0])

        self.reached_source_list = list(reached_source_set)

        # 在下游中有对应上游source点的sink点
        if not self.used_fun_map or not reached_source_set:
            return []
        for node, neighbors in self.used_fun_map.items():
            for neighbor in neighbors:
                if neighbor in self.reached_source_list and node not in self.reached_sink_list:
                    self.reached_sink_list.append(node)

        return self.reached_sink_list


def extract_keys_with_prefix(call_gragh, prefix_list):
    extracted_keys = []
    all_nodes = set()
    for node, neighbors in call_gragh.items():
        all_nodes.add(node)
        all_nodes.update(neighbors)

    for node in all_nodes:
        for prefix in prefix_list:
            if node.startswith(prefix + '.'):
                extracted_keys.append(node)

    extracted_keys = [keys for keys in extracted_keys if '.' in keys]
    return list(set(extracted_keys))


def find_used_node_in_call_gragh(call_gragh, used_fun_list):
    # 去除漏洞函数结尾的.   数据集中有一些以.结尾     例如urllib3.util.url.parse_url.
    used_fun_list = [item[:-1] if item.endswith('.') else item for item in used_fun_list]
    # 去除漏洞函数前面的/      例如src/urllib3.util.url.parse_url.
    used_fun_list = [
        item.split('/')[-1]
        for item in used_fun_list
    ]
    used_fun_list = [
        item.replace('__init__.', '', 1)
        if item.startswith('__init__.')
        else item
        for item in used_fun_list
    ]
    # 整合图中所有的节点
    all_nodes = set()
    for node, neighbors in call_gragh.items():
        all_nodes.add(node)
        all_nodes.update(neighbors)

    used_fun_dict = {}
    # 存在相同函数或者类
    for used_fun in used_fun_list:
        used_fun_dict[used_fun] = []
        for call_point in all_nodes:
            if call_point.endswith(used_fun):
                used_fun_dict[used_fun].append(call_point)

    # 不存在相同函数或者类，找函数或类中的定义
    for used_fun in used_fun_list:
        if used_fun_dict[used_fun] != []:
            continue
        for call_point in all_nodes:
            if set(used_fun.split('.')).issubset(set(call_point.split('.'))):
                used_fun_dict[used_fun].append(call_point)

    # 对列表存在包含关系的进行处理
    _used_point_list = [item for keys in used_fun_dict.values() for item in keys]
    used_point_list = []
    for used_point1 in _used_point_list:
        is_suffix = False
        for used_point2 in _used_point_list:
            if used_point2 != used_point1 and used_point2.endswith(used_point1):
                is_suffix = True
                break
        if not is_suffix:
            used_point_list.append(used_point1)

    for used_fun in used_fun_dict:
        used_fun_dict[used_fun] = list(set(used_fun_dict[used_fun]) & set(used_point_list))

    return used_point_list, used_fun_dict
