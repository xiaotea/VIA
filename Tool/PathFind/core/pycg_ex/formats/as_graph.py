#
# Copyright (c) 2021 Vitalis Salis.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from ..utils import constants
from .base import BaseFormatter


class AsGraph(BaseFormatter):
    def __init__(self, cg_generator):
        self.cg_generator = cg_generator
        self.output = {}
        self.out_types = [
            constants.FUN_DEF,
            constants.CLS_DEF,
            constants.EXT_DEF,
            constants.EXT_FUN_DEF,
            constants.EXT_CLS_DEF,
            constants.NAME_DEF,
        ]
        self.scope_tem = set()

    def get_output_key(self, key):
        if key in self.output:
            return self.output[key]
        else:
            return None

    def add_graph_import_age(self):
        def add_outgraph(key, value):
            # 在导出图中添加对应的边
            if key not in self.output:
                self.output[key] = []
            if value not in self.output[key]:
                self.output[key].append(value)
            if value not in self.output:
                self.output[value] = []

        def get_import_scope_names(scope_name):
            if scope_name in self.scope_tem:
                return
            self.scope_tem.add(scope_name)
            if scope_name not in self.cg_generator.scope_manager.get_scopes():
                return
            for key_def in self.cg_generator.scope_manager.scopes[scope_name].defs:
                if key_def.startswith('_'):
                    continue
                if self.cg_generator.scope_manager.scopes[scope_name].able_to_call != []:
                    if scope_name + '.' + key_def not in self.cg_generator.scope_manager.scopes[
                        scope_name].able_to_call:
                        continue

                if self.cg_generator.scope_manager.scopes[scope_name].defs[key_def].def_type in self.out_types:
                    get_import_scope_names(scope_name + '.' + key_def)

        def get_import_scope_name(ns_pre, import_dict):
            level = import_dict['level']
            import_str = import_dict['import_str']
            # is_all_import = False
            if import_str.endswith('.*'):
                import_str = import_str[:-2]
                # is_all_import = True

            if level == 0:
                # 传递导入未考虑
                _ns_pre = ns_pre
                while not '@' in _ns_pre.split('.')[-1] and '.' in _ns_pre:
                    full_import_str = _ns_pre + '.' + import_str
                    if self.cg_generator.scope_manager.get_scope(full_import_str):
                        return self.cg_generator.scope_manager.get_scope(full_import_str)
                    else:
                        _ns_pre = '.'.join(_ns_pre.split('.')[:-1])
                return None
            else:
                if len(ns_pre.split('.')) < level:
                    return None
                if import_dict['is_init_mod']:
                    level = level - 1
                if level == 0:
                    ns_pre_name = ns_pre
                else:
                    ns_pre_name = '.'.join(ns_pre.split('.')[:-level])
                ns_name = ns_pre_name + '.' + import_str

                if self.cg_generator.scope_manager.get_scope(ns_name):
                    return self.cg_generator.scope_manager.get_scope(ns_name)
                else:
                    # 传递导入未考虑
                    return None

        for key, items in self.cg_generator.import_manager.imports_index.items():
            # 遍历对应的文件模块，key为文件
            for item in items:
                # item为文件模块中导入的模块 {'file_mod': None, 'import_str': 'asyncio', 'level': 0}

                # c模块  from a import b  添加c ---- a.b
                # add_outgraph(key, item['import_str'])

                module_tg = key

                # 存在.*去掉.*
                import_str = item['import_str'][:-2] if item['import_str'].endswith('.*') else item['import_str']

                # c模块  from a import b 处理为c.b   未考虑from a import  b.c
                import_tgt_str = key + '.' + import_str.split('.')[-1]

                # import_scope_ns: 查找导入模块的scope命名空间
                import_scope_ns = get_import_scope_name(key, item)

                if import_scope_ns:
                    # 导入命名空间所有的命名

                    # 去掉结尾的部分
                    import_prefix = import_scope_ns.fullns[:-len(import_str.split('.')[-1])]

                    if import_tgt_str == import_scope_ns.fullns:
                        # 在a模块的init文件中 import b   相当于建立 a.b -- a.b ，无意义
                        continue

                    add_outgraph(import_tgt_str, import_scope_ns.fullns)

                    self.scope_tem = set()
                    get_import_scope_names(import_scope_ns.fullns)
                    for _import_name in self.scope_tem:
                        if _import_name.startswith(import_prefix):
                            _import_ns_str = _import_name.removeprefix(import_prefix)
                        else:
                            print('error')
                            continue
                        add_outgraph(import_tgt_str + '.' + _import_ns_str,
                                     import_scope_ns.fullns + '.' + _import_ns_str)

                else:
                    add_outgraph(import_tgt_str, import_str)

        return

    def generate(self):

        graph = self.cg_generator.get_as_graph()
        cg_simple = self.cg_generator.output()
        for node in cg_simple:
            cg_simple[node] = list(cg_simple[node])

        cg_def = {}
        for key, defi in graph:
            cg_def[key] = list(defi.get_name_pointer().get().copy())
            # if defi.def_type in out_types:
            #     print(key,defi.def_type)
            #     print(list(defi.get_name_pointer().get().copy()))

        for key in set(cg_simple.keys()) | set(cg_def.keys()):
            if key not in cg_def:
                self.output[key] = cg_simple[key]
            elif key not in cg_simple:
                self.output[key] = cg_def[key]
            else:
                self.output[key] = list(set(cg_simple[key] + cg_def[key]))

        # for key1 in set(cg_def.keys()) - set(cg_simple.keys()):
        #     if '.' not in key1:
        #         continue
        #     for key2 in self.output.keys():
        #         if key1 != key2 and key2.endswith('.' + key1) and key1 not in self.output[key2] and key2 not in \
        #                 self.output[key1]:
        #             self.output[key1].append(key2)

        self.add_graph_import_age()

        return self.output
