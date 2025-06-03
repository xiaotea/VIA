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
import ast
import os
from .. import utils
from ..machinery.definitions import Definition
from .base import ProcessingBase


class PreProcessor(ProcessingBase):
    def __init__(
        self,
        filename,
        modname,
        import_manager,
        scope_manager,
        def_manager,
        class_manager,
        module_manager,
        modules_analyzed=None,
    ):
        super().__init__(filename, modname, modules_analyzed)

        self.modname = modname
        self.mod_dir = os.sep.join(self.filename.split(os.sep)[:-1])

        self.import_manager = import_manager
        self.scope_manager = scope_manager
        self.def_manager = def_manager
        self.class_manager = class_manager
        self.module_manager = module_manager

    def _get_fun_defaults(self, node):
        defaults = {}

        start = len(node.args.args) - len(node.args.defaults)
        if len(node.args.args) == 0:
            return defaults

        for cnt, d in enumerate(node.args.defaults, start=start):
            if not d:
                continue

            self.visit(d)
            defaults[node.args.args[cnt].arg] = self.decode_node(d)

        start = len(node.args.kwonlyargs) - len(node.args.kw_defaults)
        for cnt, d in enumerate(node.args.kw_defaults, start=start):
            if not d:
                continue
            self.visit(d)
            defaults[node.args.kwonlyargs[cnt].arg] = self.decode_node(d)

        return defaults

    def analyze_submodule(self, modname):
        super().analyze_submodule(
            PreProcessor,
            modname,
            self.import_manager,
            self.scope_manager,
            self.def_manager,
            self.class_manager,
            self.module_manager,
            modules_analyzed=self.get_modules_analyzed(),
        )

    def visit_Module(self, node):
        def iterate_mod_items(items, const):
            for item in items:
                defi = self.def_manager.get(item)
                if not defi:
                    defi = self.def_manager.create(item, const)

                splitted = item.split(".")
                name = splitted[-1]
                parentns = ".".join(splitted[:-1])
                self.scope_manager.get_scope(parentns).add_def(name, defi)

        self.import_manager.set_current_mod(self.modname, self.filename)

        #添加模块
        mod = self.module_manager.create(self.modname, self.filename)

        first = 1
        #代码行数
        last = len(self.contents.splitlines())
        if last == 0:
            first = 0
        mod.add_method(self.modname, first, last)

        root_sc = self.scope_manager.get_scope(self.modname)
        if not root_sc:
            # initialize module scopes
            #items 为当前环境中的类、函数set集合 {‘classes’:[],'functions':[],'export_symtable':[]}
            items = self.scope_manager.handle_module(
                self.modname, self.filename, self.contents
            )

            root_sc = self.scope_manager.get_scope(self.modname)
            root_defi = self.def_manager.get(self.modname)
            if not root_defi:
                root_defi = self.def_manager.create(
                    self.modname, utils.constants.MOD_DEF
                )
            root_sc.add_def(self.modname.split(".")[-1], root_defi)

            # create function and class defs and add them to their scope
            # we do this here, because scope_manager doesn't have an
            # interface with def_manager, and we want function definitions
            # to have the correct points_to set
            iterate_mod_items(items["functions"], utils.constants.FUN_DEF)
            iterate_mod_items(items["classes"], utils.constants.CLS_DEF)
            iterate_mod_items(items["export_symtable"], utils.constants.EXT_CLS_DEF)
            if items["export_symtable"] != []:
                self.scope_manager.get_scope(self.modname).create_able_to_call(items["export_symtable"])

        defi = self.def_manager.get(self.modname)
        if not defi:
            defi = self.def_manager.create(self.modname, utils.constants.MOD_DEF)

        super().visit_Module(node)


    def visit_Import(self, node, prefix="", level=0):
        # if  "test" in self.import_manager.current_module:
        #     if hasattr(node,"module"):
        #         print(node.module,prefix,level )
        """
        处理 import 语句的方法
        module 不再  node里面
        node.names.列表编号.name 
        
        处理from  import 语句的方法
        对于形式如 `from something import anything` 的导入，prefix 被设置成 "something"
        对于形式如 `from .relative import anything` 的导入，level 被设置成一个数字，表示父目录的层数（比如在这种情况下 level=1）
        """

        # 处理导入的模块名
        def handle_src_name(name):
            # 获取模块名并在必要时添加前缀
            src_name = name
            if prefix:
                src_name = prefix + "." + src_name
            return src_name

        # 处理作用域
        def handle_scopes(imp_name, tgt_name, modname):
            # 创建定义
            def create_def(scope, name, imported_def):
                if name not in scope.get_defs():
                    # 在当前域中加入导入名字 当前域testing_utils  from .file_utils import  available   --> file_utils.available   testing_utils.available
                    # 先创建def_manager 的定义，再添加 对应的域
                    def_ns = utils.join_ns(scope.get_ns(), name)
                    defi = self.def_manager.get(def_ns)
                    if not defi:
                        defi = self.def_manager.assign(def_ns, imported_def)
                    defi.get_name_pointer().add(imported_def.get_ns())
                    current_scope.add_def(name, defi)

            current_scope = self.scope_manager.get_scope(self.current_ns)
            imported_scope = self.scope_manager.get_scope(modname)
            if tgt_name == "*":
                # 如果是通配符导入，则将所有定义复制到当前作用域
                for name, defi in imported_scope.get_defs().items():
                    create_def(current_scope, name, defi)
                    current_scope.get_def(name).get_name_pointer().add(defi.get_ns())
            else:
                # 如果在导入的作用域中存在则复制它
                defi = imported_scope.get_def(imp_name)
                if not defi:
                    # 如果作用域没有，说明该文件还未分析，查找导入域
                    defi = self.def_manager.get(imp_name)

                if defi:
                    create_def(current_scope, tgt_name, defi)
                    current_scope.get_def(tgt_name).get_name_pointer().add(
                        defi.get_ns()
                    )
        def add_imoprts_index(mod_dir, import_str,level,imported_name,is_init_file):
            self.import_manager.set_imports_index(mod_dir, import_str,level,imported_name,is_init_file)

        # 添加外部定义
        def add_external_def(name, target):
            # 处理外部导入，例如: "import package.module.module...
            # 我们希望将其视为: "import package"，并在定义管理器中保存为这样
            # if (name == target) & (len(name.split(".")) > 1):
            #     name = name.split(".")[0]
            #     target = target.split(".")[0]
            # 添加一个外部定义
            defi = self.def_manager.get(name)
            if not defi:
                defi = self.def_manager.create(name, utils.constants.EXT_DEF)
            scope = self.scope_manager.get_scope(self.current_ns)
            if target != "*":
                # 为目标添加一个指向该名称空间的定义
                tgt_ns = utils.join_ns(scope.get_ns(), target)
                tgt_defi = self.def_manager.get(tgt_ns)
                if not tgt_defi:
                    tgt_defi = self.def_manager.create(tgt_ns, utils.constants.EXT_DEF)
                tgt_defi.get_name_pointer().add(defi.get_ns())
                scope.add_def(target, tgt_defi)

        is_init_file = self.import_manager._is_init_file()
        # 遍历导入的每个项
        for import_item in node.names:
            src_name = handle_src_name(import_item.name)
            tgt_name = import_item.asname if import_item.asname else import_item.name
            print('---',src_name, tgt_name,level)
            imported_name = None
            if level == 0 :
                if src_name in self.import_manager.module_imports :
                    imported_name = src_name
                else:
                    if src_name in self.import_manager.module_not_found_set:
                        return
            if not imported_name:
                imported_name = self.import_manager.handle_import(src_name, level)
            add_imoprts_index(self.import_manager.current_module, src_name, level, imported_name, is_init_file)

            if self.import_manager.current_module.split('.')[-1] == src_name.split('.')[0]:
                # 若模块中自己导入自己，则处理为外部导入
                add_external_def(src_name, tgt_name)
                continue


            if not imported_name:
                self.import_manager.module_not_found_set.add(src_name)
                # 处理外部导入
                add_external_def(src_name, tgt_name)
                continue

            fname = self.import_manager.get_filepath(imported_name)
            if not fname:
                # 处理外部导入
                add_external_def(src_name, tgt_name)
                continue
            # 只分析当前目录下的模块
            if self.import_manager.get_mod_dir() in fname: #如果模块是当前分析文件下的，加入待分析列表

                if imported_name not in self.modules_analyzed:
                    self.analyze_submodule(imported_name)
                handle_scopes(import_item.name, tgt_name, imported_name)
            else:
                # 处理外部导入
                add_external_def(src_name, tgt_name)

        # 处理未被分析的所有模块
        for modname in self.import_manager.get_imports(self.modname):
            fname = self.import_manager.get_filepath(modname)

            if not fname:
                continue
            # 只分析当前目录下的模块
            if (
                    self.import_manager.get_mod_dir() in fname
                    and modname not in self.modules_analyzed
            ):
                self.analyze_submodule(modname)

    def visit_ImportFrom(self, node):
        self.visit_Import(node, prefix=node.module, level=node.level)

    def _get_last_line(self, node):
        lines = sorted(
            list(ast.walk(node)),
            key=lambda x: x.lineno if hasattr(x, "lineno") else 0,
            reverse=True,
        )
        if not lines:
            return node.lineno

        last = getattr(lines[0], "lineno", node.lineno)
        if last < node.lineno:
            return node.lineno

        return last

    def _handle_function_def(self, node, fn_name):
        current_def = self.def_manager.get(self.current_ns)

        defaults = self._get_fun_defaults(node)

        fn_def = self.def_manager.handle_function_def(self.current_ns, fn_name)

        mod = self.module_manager.get(self.modname)
        if not mod:
            mod = self.module_manager.create(self.modname, self.filename)
        mod.add_method(fn_def.get_ns(), node.lineno, self._get_last_line(node))

        defs_to_create = []
        name_pointer = fn_def.get_name_pointer()

        # TODO: static methods can be created using
        # the staticmethod() function too
        is_static_method = False
        if hasattr(node, "decorator_list"):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Name)
                    and decorator.id == utils.constants.STATIC_METHOD
                ):
                    is_static_method = True

        if (
            current_def.get_type() == utils.constants.CLS_DEF
            and not is_static_method
            and node.args.args
        ):
            arg_ns = utils.join_ns(fn_def.get_ns(), node.args.args[0].arg)
            arg_def = self.def_manager.get(arg_ns)
            if not arg_def:
                arg_def = self.def_manager.create(arg_ns, utils.constants.NAME_DEF)
            arg_def.get_name_pointer().add(current_def.get_ns())

            self.scope_manager.handle_assign(
                fn_def.get_ns(), arg_def.get_name(), arg_def
            )
            node.args.args = node.args.args[1:]

        for pos, arg in enumerate(node.args.args):
            arg_ns = utils.join_ns(fn_def.get_ns(), arg.arg)
            name_pointer.add_pos_arg(pos, arg.arg, arg_ns)
            defs_to_create.append(arg_ns)

        for arg in node.args.kwonlyargs:
            arg_ns = utils.join_ns(fn_def.get_ns(), arg.arg)
            # TODO: add_name_arg function
            name_pointer.add_name_arg(arg.arg, arg_ns)
            defs_to_create.append(arg_ns)

        # TODO: Add support for kwargs and varargs
        # if node.args.kwarg:
        #    pass
        # if node.args.vararg:
        #    pass

        for arg_ns in defs_to_create:
            arg_def = self.def_manager.get(arg_ns)
            if not arg_def:
                arg_def = self.def_manager.create(arg_ns, utils.constants.NAME_DEF)

            self.scope_manager.handle_assign(
                fn_def.get_ns(), arg_def.get_name(), arg_def
            )

            # has a default
            arg_name = arg_ns.split(".")[-1]
            if defaults.get(arg_name, None):
                for default in defaults[arg_name]:
                    if isinstance(default, Definition):
                        arg_def.get_name_pointer().add(default.get_ns())
                        if default.is_function_def():
                            arg_def.get_name_pointer().add(default.get_ns())
                        else:
                            arg_def.merge(default)
                    else:
                        arg_def.get_lit_pointer().add(default)
        return fn_def

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_FunctionDef(self, node):
        self._handle_function_def(node, node.name)

        super().visit_FunctionDef(node)

    def visit_For(self, node):
        # just create the definition for target
        if isinstance(node.target, ast.Name):
            target_ns = utils.join_ns(self.current_ns, node.target.id)
            if not self.def_manager.get(target_ns):
                defi = self.def_manager.create(target_ns, utils.constants.NAME_DEF)
                self.scope_manager.get_scope(self.current_ns).add_def(
                    node.target.id, defi
                )
        super().visit_For(node)

    def visit_Assign(self, node):
        self._visit_assign(node.value, node.targets)

    def visit_Return(self, node):
        self._visit_return(node)

    def visit_Yield(self, node):
        self._visit_return(node)

    def visit_Call(self, node):
        self.visit(node.func)
        # if it is not a name there's nothing we can do here
        # ModuleVisitor will be able to resolve those calls
        # since it'll have the name tracking information
        if not isinstance(node.func, ast.Name):
            return

        utils.join_ns(self.current_ns, node.func.id)

        defi = self.scope_manager.get_def(self.current_ns, node.func.id)
        if not defi:
            return

        if defi.get_type() == utils.constants.CLS_DEF:
            defi = self.def_manager.get(
                utils.join_ns(defi.get_ns(), utils.constants.CLS_INIT)
            )
            if not defi:
                return

        self.iterate_call_args(defi, node)

    def visit_Lambda(self, node):
        # The name of a lambda is defined by the counter of the current scope
        current_scope = self.scope_manager.get_scope(self.current_ns)
        lambda_counter = current_scope.inc_lambda_counter()
        lambda_name = utils.get_lambda_name(lambda_counter)
        lambda_full_ns = utils.join_ns(self.current_ns, lambda_name)

        # create a scope for the lambda
        self.scope_manager.create_scope(lambda_full_ns, current_scope)
        lambda_def = self._handle_function_def(node, lambda_name)
        # add it to the current scope
        current_scope.add_def(lambda_name, lambda_def)

        super().visit_Lambda(node, lambda_name)

    def visit_ClassDef(self, node):
        # create a definition for the class (node.name)
        cls_def = self.def_manager.handle_class_def(self.current_ns, node.name)

        mod = self.module_manager.get(self.modname)
        if not mod:
            mod = self.module_manager.create(self.modname, self.filename)
        mod.add_method(cls_def.get_ns(), node.lineno, self._get_last_line(node))

        # iterate bases to compute MRO for the class
        cls = self.class_manager.get(cls_def.get_ns())
        if not cls:
            cls = self.class_manager.create(cls_def.get_ns(), self.modname)

        super().visit_ClassDef(node)

    def analyze(self):
        if not self.import_manager.get_node(self.modname):
            # 给导入的模块创建节点
            self.import_manager.create_node(self.modname)

            #给导入的模块关联到对应的路径
            self.import_manager.set_filepath(self.modname, self.filename)
        try:
            ast_tree = ast.parse(self.contents, self.filename)
        except :
            # 抽象语法树解析失败
            return
        self.visit(ast_tree)
