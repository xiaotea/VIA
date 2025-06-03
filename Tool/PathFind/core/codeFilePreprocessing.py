import datetime
import os
import platform
import shutil
import subprocess
import time

# pyc  反编译
# pyi  pyx  pyw   直接改后缀


pycdc_path = os.sep.join(['.', 'tool', 'fileDealTool'])
pycdc_path = os.path.abspath(pycdc_path)

current_os = platform.system()
if current_os == 'Windows':
    pycdc_command = pycdc_path + os.sep + 'pycdc.exe'  # or the full path to pycdc.exe
else:
    pycdc_command = pycdc_path + os.sep + 'pycdc'


def write_file(new_file_path, content):
    with open(new_file_path, "w") as file:
        file.write(content)


def file_exist(file_path):
    if not os.path.isfile(file_path):
        return
    base_name = os.path.splitext(file_path)[0]
    new_file_path = f"{base_name}.py"
    if os.path.isfile(new_file_path):
        return
    return  new_file_path

def pyc_file_decompy(file_path):
    new_file_path = file_exist(file_path)
    if not new_file_path:
        return
    result = subprocess.run(pycdc_command + ' ' + file_path, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True)
    content = result.stdout
    write_file(new_file_path, content)

def py_other_file_deal(file_path):
    new_file_path = file_exist(file_path)
    if not new_file_path:
        return

    try:
        shutil.copyfile(file_path, new_file_path)
    except IOError as e:
        print(f"{file_path}文件复制失败: {e}")



def other_py_file_deal(file_path):
    '''
    处理所有的pyc、pyx、pyi、pyw文件，
    pyc反编译为源码pyx、pyi、pyw文件重命名
    '''
    if file_path.endswith(('.pyx', '.pyi', '.pyw')):
        py_other_file_deal(file_path)
    elif file_path.endswith('.pyc'):
        if '__pycache__' in file_path:
            return
        pyc_file_decompy(file_path)


# starttime = time.time()
# other_py_file_deal(r'C:\Users\86152\Desktop\pycdc\build\Debug\pycg.cpython-310.pyc')
# endtime = time.time()
# timelength = endtime - starttime
# # 格式化时间长度为易读的格式
# formatted_time = str(datetime.timedelta(seconds=timelength))
# print(f"处理时间为: {formatted_time}")
