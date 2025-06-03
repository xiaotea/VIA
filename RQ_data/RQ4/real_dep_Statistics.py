# 加载数据
import json
import matplotlib.pyplot as plt
import numpy as np


# 绘制漏洞依赖路径随着真实依赖路径长度的变化趋势


with open('../ctx', 'r') as f:
    analyze_data = json.load(f)

path_len_dict = {}


reachable_dep_num,unreachable_dep_num, =  0,0
reachable_2length = []

for triple_name in analyze_data:
    # if "CVE-2023-43665@django@4.2.5@haupt@2.0.0rc40" != triple_name:
    #     continue

    triple_dict = analyze_data[triple_name]
    if triple_dict["is_reachable"]:
        reachable_dep_num+=1
    else:
        unreachable_dep_num+=1
    if 2 in triple_dict["path_length_list"] :
        if triple_dict["is_reachable"]:
            reachable_2length.append(1)
        else:
            reachable_2length.append(0)

    # fun_path_info = triple_dict['fun_path_info']
    # for index, path_lenth in enumerate(triple_dict["path_length_list"]):
    #     add_flag = 1
    #
    #     if path_lenth not in path_len_dict:
    #         path_len_dict[path_lenth] = []
    #     if len(fun_path_info[str(index)]) != path_lenth - 1:
    #         add_flag = 0
    #         path_len_dict[path_lenth].append(add_flag)
    #         break
    #     for duplet, duplet_dict in fun_path_info[str(index)].items():
    #         if len(duplet_dict.get("path_num_list", [])) == 0:
    #             add_flag = 0
    #             break
    #     path_len_dict[path_lenth].append(add_flag)


print(reachable_dep_num,unreachable_dep_num,reachable_dep_num/(reachable_dep_num+unreachable_dep_num))
print(reachable_2length.count(1)/len(reachable_2length),len(reachable_2length))







