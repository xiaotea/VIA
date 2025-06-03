from pylint.lint import Run
from pylint.reporters.text import TextReporter
import io
from lib2to3.refactor import RefactoringTool, get_fixers_from_package
import ast
# 获取所有可用的 fixers
fixers = get_fixers_from_package('lib2to3.fixes')

# 初始化 RefactoringTool
refactor_tool = RefactoringTool(fixers)

# apply_list = ['lib2to3.fixes.fix_except','lib2to3.fixes.fix_exec','lib2to3.fixes.fix_print','lib2to3.fixes.fix_raise','lib2to3.fixes.fix_standarderror','lib2to3.fixes.fix_throw','lib2to3.fixes.fix_ws_comma',]
# #filter_list = ['lib2to3.fixes.fix_apply', 'lib2to3.fixes.fix_asserts', 'lib2to3.fixes.fix_basestring', 'lib2to3.fixes.fix_buffer', 'lib2to3.fixes.fix_dict', 'lib2to3.fixes.fix_except', 'lib2to3.fixes.fix_exec', 'lib2to3.fixes.fix_execfile', 'lib2to3.fixes.fix_exitfunc', 'lib2to3.fixes.fix_filter', 'lib2to3.fixes.fix_funcattrs', 'lib2to3.fixes.fix_future', 'lib2to3.fixes.fix_getcwdu', 'lib2to3.fixes.fix_has_key', 'lib2to3.fixes.fix_idioms', 'lib2to3.fixes.fix_import', 'lib2to3.fixes.fix_imports', 'lib2to3.fixes.fix_imports2', 'lib2to3.fixes.fix_input', 'lib2to3.fixes.fix_intern', 'lib2to3.fixes.fix_isinstance', 'lib2to3.fixes.fix_itertools', 'lib2to3.fixes.fix_itertools_imports', 'lib2to3.fixes.fix_long', 'lib2to3.fixes.fix_map', 'lib2to3.fixes.fix_metaclass', 'lib2to3.fixes.fix_methodattrs', 'lib2to3.fixes.fix_ne', 'lib2to3.fixes.fix_next', 'lib2to3.fixes.fix_nonzero', 'lib2to3.fixes.fix_numliterals', 'lib2to3.fixes.fix_operator', 'lib2to3.fixes.fix_paren', 'lib2to3.fixes.fix_print', 'lib2to3.fixes.fix_raise', 'lib2to3.fixes.fix_raw_input', 'lib2to3.fixes.fix_reduce', 'lib2to3.fixes.fix_reload', 'lib2to3.fixes.fix_renames', 'lib2to3.fixes.fix_repr', 'lib2to3.fixes.fix_set_literal', 'lib2to3.fixes.fix_standarderror', 'lib2to3.fixes.fix_sys_exc', 'lib2to3.fixes.fix_throw', 'lib2to3.fixes.fix_tuple_params', 'lib2to3.fixes.fix_types', 'lib2to3.fixes.fix_unicode', 'lib2to3.fixes.fix_urllib', 'lib2to3.fixes.fix_ws_comma', 'lib2to3.fixes.fix_xrange', 'lib2to3.fixes.fix_xreadlines', 'lib2to3.fixes.fix_zip']
#
# fixers = list(set(fixers) & set(apply_list))

def is_python2_code(filepath):
    #判断是否是python2代码
    #使用抽象语法树

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            file_code = f.read()
        ast.parse(file_code)
        return False
    except Exception as e :
        return True

    # 方法2
    # output = io.StringIO()
    # reporter = TextReporter(output)
    #
    # # Run pylint analysis
    # Run([filepath], reporter=reporter, exit=False)
    #
    # # Check for Python 2 specific issues in the output
    # output_content = output.getvalue()
    # return 'SyntaxError' in output_content or 'invalid syntax' in output_content or 'syntax-error' in output_content

def change_code(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source_code = file.read()
        new_code = refactor_tool.refactor_string(source_code, file_path)
    except Exception as e:
        return
    # 写回文件
    with open(file_path, 'w',encoding='utf-8') as file:
        file.write(str(new_code))


def change_python_file_2_to_3(filepath):
    if is_python2_code(filepath):
        change_code(filepath)
        return True
    return False



def change_pyfile_list_2_to_3(python_code_file_list):
    return_flag = False # 标志: 该目录内文件是否有改变
    for filepath in python_code_file_list:
        if change_python_file_2_to_3(filepath):
            return_flag = True
    return return_flag
