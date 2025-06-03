import ast
import logging
import os
import traceback
# from ..utils.utils import output_errors

output_errors = True
def extract_imported_module(content):
    imported_modules = []
    try:
        tree = ast.parse(content)
    except:
        return imported_modules

    variables = {}
    for node in ast.walk(tree):

        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Str):
            variable_name = node.targets[0].id
            variable_value = node.value.s
            variables[variable_name] = variable_value

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "importlib" and node.func.attr == "import_module":
            if not node.args:
                continue
            if isinstance(node.args[0], ast.Name):
                # If the argument is a variable name
                variable_name = node.args[0].id
                if variable_name in variables:
                    print(variables.get(variable_name))
                    imported_modules.append(variables.get(variable_name))
            elif isinstance(node.args[0], ast.Str):
                # If the argument is a string literal
                module_name = node.args[0].s
                imported_modules.append(module_name)
    return imported_modules

def get_all_imports(file_name, extra_ignore_dirs=None, follow_links=True,dynamic_analyze=True):
    imports = set()
    raw_imports = set()
    candidates = []

    with open(file_name, "rt", errors="replace") as f:
        contents = f.read()

    if dynamic_analyze and 'importlib.import_module' in contents:
        dynamic_import_list = extract_imported_module(contents)
        raw_imports.update(dynamic_import_list)

    try:
        tree = ast.parse(contents, file_name)
        # 对要分析的文件解析为抽象语法树
        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                # 识别import
                for subnode in node.names:
                    raw_imports.add(subnode.name)
            elif isinstance(node, ast.ImportFrom):
                # 识别from import
                raw_imports.add(node.module)
    except Exception as exc:
        if output_errors:
            print(exc)
            logging.warning("Failed on file: %s" % file_name)
            return []
        else:
            return []
            # logging.error("Failed on file: %s" % file_name)

    # Clean up imports
    for name in [n for n in raw_imports if n]:
        # 提取第一部分  bs4.formatter  -->bs4
        cleaned_name, _, _ = name.partition('.')
        imports.add(cleaned_name)

    packages = imports - (set(candidates) & imports)
    logging.debug('Found packages: {0}'.format(packages))

    # 筛出掉标准库中的库
    with open(join("stdlib"), "r") as f:
        data = {x.strip() for x in f}

    return list(packages - data)


def join(f):
    return os.path.join(os.path.dirname(__file__), f)


def get_pkg_names(pkgs):
    """Get PyPI package names from a list of imports.

    Args:
        pkgs (List[str]): List of import names.

    Returns:
        List[str]: The corresponding PyPI package names.

    """
    result = set()
    # 找到
    with open(join("mapping"), "r") as f:
        data = dict(x.strip().split(":") for x in f)
    for pkg in pkgs:
        # Look up the mapped requirement. If a mapping isn't found,
        # simply use the package name.

        # dict.get() 第二个参数是取键值对的值，娶不到就用第二个参数的数值
        result.add(data.get(pkg, pkg))
    # Return a sorted list for backward compatibility.
    return sorted(result, key=lambda s: s.lower())


def get_locally_installed_packages(pythonVenvPath, encoding="utf-8"):
    # 遍历本地安装目录，查找安装的组件版本
    # 查询规则根据安装文件top_level.txt查询组件及其版本信息
    #
    packages = []
    ignore = ["tests", "_tests", "egg", "EGG", "info"]
    for path in pythonVenvPath:
        for root, dirs, files in os.walk(path):
            for item in files:
                if "top_level" in item:
                    # print(item)
                    item = os.path.join(root, item)
                    with open(item, "r", encoding=encoding) as f:
                        package = root.split(os.sep)[-1].split("-")
                        try:
                            top_level_modules = f.read().strip().split("\n")
                        except Exception as e:  # NOQA
                            # TODO: What errors do we intend to suppress here?
                            continue
                        # 收集过滤掉的模块
                        # filter off explicitly ignored top-level modules
                        # such as test, egg, etc.
                        filtered_top_level_modules = list()

                        for module in top_level_modules:
                            if (
                                    # 确保本身和top_level文件中的都不在忽略名单中
                                    (module not in ignore) and
                                    (package[0] not in ignore)
                            ):
                                # append exported top level modules to the list
                                filtered_top_level_modules.append(module)

                        version = None
                        if len(package) > 1:
                            version = package[1].replace(
                                ".dist", "").replace(".egg", "")

                        # append package: top_level_modules pairs
                        # instead of top_level_module: package pairs
                        packages.append({
                            'name': package[0],
                            'version': version,
                            'exports': filtered_top_level_modules
                        })
    return packages


def get_import_local(imports, pythonVenvPath, encoding='utf-8'):
    local = get_locally_installed_packages(pythonVenvPath, encoding)
    result = []
    for item in imports:
        # search through local packages
        for package in local:
            # if candidate import name matches export name
            # or candidate import name equals to the package name
            # append it to the result
            if item in package['exports'] or item == package['name']:
                # 筛除egg等包
                result.append(package)

    # removing duplicates of package/version
    # had to use second method instead of the previous one,
    # because we have a list in the 'exports' field
    # https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
    result_unique = [i for n, i in enumerate(result) if i not in result[n + 1:]]

    result_unique_version = {package.get('name'): package.get('version')
                             for package in local
                             if package.get('name') in result_unique and package.get('version') != None}

    return result_unique_version



def get_used_pckages(path_list,dynamic_analyze=True):
    import_pkgdir_list = []
    for pkg_path in path_list:
        import_pkgdir_list = import_pkgdir_list + get_all_imports(pkg_path,dynamic_analyze=dynamic_analyze)

    return list(set(import_pkgdir_list))


# # alist1 = get_used_pckages([r'C:\python_project\data\athena@0.5.0\athena-0.5.0'],dynamic_analyze=False)
# alist2 = get_used_pckages([r'C:\python_project\data\athena@0.5.0\athena-0.5.0\athena\utils\ssh.py'],dynamic_analyze=True)
# # print(alist1)
# print(alist2)