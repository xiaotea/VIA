import json
from collections import Counter

from utils import find_all_files_in_folder


def non_zero_mode(numbers):
    # 过滤掉0
    non_zero_numbers = [num for num in numbers if num != 0 and num != 2]
    # 使用Counter统计出现次数
    counter = Counter(non_zero_numbers)
    # 找出最大频率的数字
    max_freq = max(counter.values())
    # 找出最大频率对应的数字（可能有多个）
    modes = [num for num, freq in counter.items() if freq == max_freq]
    return modes


def analyze(dependency_path):
    info = {}
    info['path_len'] = 0  # 依赖路径数目
    info['max_len'] = 0  # 最长依赖链条
    info['is_direct_den'] = -1  # 0直接依赖 1间接依赖 2既是又是   -1 没有依赖关系
    info['path_len_list'] = []

    if dependency_path == []:
        info['path_len'] = 0
        info['is_direct_den'] = -1
        info['max_len'] = 0

        return info
    info['path_len'] = len(dependency_path)

    for path in dependency_path:
        info['path_len_list'].append(len(path))
        if len(path) > info['max_len']:
            info['max_len'] = len(path)

        if len(path) == 2:
            if info['is_direct_den'] == 2:
                continue
            elif info['is_direct_den'] == -1:
                info['is_direct_den'] = 0
            elif info['is_direct_den'] == 1:
                info['is_direct_den'] = 2
        elif len(path) > 2:
            if info['is_direct_den'] == 2:
                continue
            elif info['is_direct_den'] == -1:
                info['is_direct_den'] = 1
            elif info['is_direct_den'] == 0:
                info['is_direct_den'] = 2
    return info


file_list = find_all_files_in_folder('/home/gf/wyj/python_test/PathFind/core/AnalyzeRes')
res_list = []

average_path_num = 0
max_path_num = 0

un_depen_num = 0
direct_num = 0
in_direct_num = 0
direct_indirect_num = 0
max_path_len = 0

aver_com_num = 0
depen_path_num_list = []

for json_file in file_list:
    # print(json_file)
    if json_file.endswith('fail_log'):
        continue
    with open(json_file, 'r') as f:
        try:
            dependency_dict = json.load(f)
        except:
            continue

    # if dependency_dict['dependency_path'] ==[]:
    #     print(json_file)
    #     print(dependency_dict['deploy_dependency'])
    # print(list(dependency_dict.keys()))

    anal_res = analyze(dependency_dict['dependency_path'])
    if anal_res['path_len'] == 8041:
        print(json_file)
    anal_res['Versionmap'] = len(dependency_dict['Versionmap'])
    # print(json_file)
    # print(dependency_dict['dependency_path'])

    info = anal_res

    aver_com_num = aver_com_num + info['Versionmap']

    max_path_len = max_path_len if max_path_len > info['path_len'] else info['path_len']
    average_path_num = average_path_num + info['path_len']
    max_path_num = max_path_num if max_path_num > info['max_len'] else info['max_len']
    if info['is_direct_den'] == -1:
        un_depen_num += 1
    if info['is_direct_den'] == 0:
        direct_num += 1
    if info['is_direct_den'] == 1:
        in_direct_num += 1
    if info['is_direct_den'] == 2:
        direct_indirect_num += 1

    res_list.append(info)
    depen_path_num_list = depen_path_num_list + info['path_len_list']

non_zero_numbers = [num for num in depen_path_num_list if num != 0 and num != 2]

print('统计依赖关系数目', len(res_list))
print('平均依赖组件数目', aver_com_num/len(res_list))
print('单个最多依赖路径条', max_path_len)
print("平均依赖路径数目", average_path_num / len(res_list))
print("最长依赖路径数目", max_path_num)
print("没有依赖关系数目", un_depen_num)
print("直接依赖关系数目", direct_num)
print("间接依赖关系数目", in_direct_num)
print("直接&间接依赖关系数目", direct_indirect_num)
print("间接依赖链众数", non_zero_mode(depen_path_num_list))

import matplotlib.pyplot as plt

# import matplotlib
# a=sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])
# for i in a:
#     print(i)
plt.rcParams['font.family'] = 'AR PL UKai CN'


def plot_histogram(numbers):
    # 使用Counter统计数字出现的次数
    counts = {}
    for num in numbers:
        if num in counts:
            counts[num] += 1
        else:
            counts[num] = 1

    # 提取数字和对应的计数
    x = list(counts.keys())
    y = list(counts.values())

    # 绘制柱状图
    plt.bar(x, y, tick_label=x, width=0.5, align='center')
    plt.bar(x, y)
    plt.xlabel('依赖长度')
    plt.ylabel('个数')
    plt.title('依赖链长度统计')

    # 在每个柱形上显示数字
    for i in range(len(x)):
        plt.text(x[i], y[i], str(y[i]), ha='center', va='bottom')

    plt.show()


plot_histogram(depen_path_num_list)
