#
# Copyright (c) 2020 Vitalis Salis.
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
import symtable
import ast
from .. import utils


class ScopeManager(object):
    """Manages the scope entries"""

    def __init__(self):
        self.scopes = {}

    #  处理文件
    def handle_module(self, modulename, filename, contents):
        functions = []
        classes = []

        def handle_export_symtable(contents):
            all_vars = []
            try:
                # 使用 ast 模块解析 Python 代码
                # 转换 contents 字符串为 AST（抽象语法树）
                tree = ast.parse(contents)
                # 遍历 AST，查找是否存在 __all__ 变量定义
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == '__all__':
                                if isinstance(node.value, ast.List):
                                    # 提取 __all__ 变量中的值
                                    all_vars = [elt.s for elt in node.value.elts if isinstance(elt, ast.Str)]
                                break
            except:
                return all_vars
            return all_vars

        def process(namespace, parent, table):
            # namespace, parent, table：命名空间，父级符号表，当前符号表对象
            if table.get_name() == "top" and table.get_lineno() == 0:
                # 检查当前符号表的名称是否为 "top"，并且行号是否为 0，可以确定当前处理的符号表是否为顶层符号表。
                name = ""
            else:
                name = table.get_name()

            if name:
                fullns = utils.join_ns(namespace, name)
            else:
                fullns = namespace

            # 判断是方法还是类
            if table.get_type() == "function":
                functions.append(fullns)

            if table.get_type() == "class":
                classes.append(fullns)

            sc = self.create_scope(fullns, parent)

            for t in table.get_children():
                process(fullns, sc, t)

        process(
            modulename, None, symtable.symtable(contents, filename, compile_type="exec")
        )
        export_symtable_list = []
        if '__all__' in contents:
            export_symtable_list = handle_export_symtable(contents)
            export_symtable_list = [utils.join_ns(modulename, _symtable) for _symtable in export_symtable_list if _symtable ]

        return {"functions": functions, "classes": classes, 'export_symtable': export_symtable_list}

    def handle_assign(self, ns, target, defi):
        scope = self.get_scope(ns)
        if scope:
            scope.add_def(target, defi)

    def get_def(self, current_ns, var_name):
        current_scope = self.get_scope(current_ns)
        while current_scope:
            defi = current_scope.get_def(var_name)
            if defi:
                return defi
            current_scope = current_scope.parent

    def get_scope(self, namespace):
        if namespace in self.get_scopes():
            return self.get_scopes()[namespace]

    def create_scope(self, namespace, parent):
        if namespace not in self.scopes:
            sc = ScopeItem(namespace, parent)
            self.scopes[namespace] = sc
        return self.scopes[namespace]

    def get_scopes(self):
        return self.scopes


class ScopeItem(object):
    def __init__(self, fullns, parent):
        if parent and not isinstance(parent, ScopeItem):
            raise ScopeError("Parent must be a ScopeItem instance")

        if not isinstance(fullns, str):
            raise ScopeError("Namespace should be a string")

        self.parent = parent
        self.defs = {}
        self.lambda_counter = 0
        self.dict_counter = 0
        self.list_counter = 0
        self.fullns = fullns
        self.able_to_call = []

    def create_able_to_call(self, able_to_call):
        self.able_to_call = able_to_call

    def get_ns(self):
        return self.fullns

    def get_defs(self):
        return self.defs

    def get_def(self, name):
        defs = self.get_defs()
        if name in defs:
            return defs[name]

    def get_lambda_counter(self):
        return self.lambda_counter

    def get_dict_counter(self):
        return self.dict_counter

    def get_list_counter(self):
        return self.list_counter

    def inc_lambda_counter(self, val=1):
        self.lambda_counter += val
        return self.lambda_counter

    def inc_dict_counter(self, val=1):
        self.dict_counter += val
        return self.dict_counter

    def inc_list_counter(self, val=1):
        self.list_counter += val
        return self.list_counter

    def reset_counters(self):
        self.lambda_counter = 0
        self.dict_counter = 0
        self.list_counter = 0

    def add_def(self, name, defi):
        self.defs[name] = defi

    def merge_def(self, name, to_merge):
        if name not in self.defs:
            self.defs[name] = to_merge
            return

        self.defs[name].merge_points_to(to_merge.get_points_to())


class ScopeError(Exception):
    pass
