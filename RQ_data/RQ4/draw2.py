import json
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import pickle

def load_analyze_data(filepath):
    """加载分析数据"""
    try:
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {filepath} was not found.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Failed to decode JSON from the file.")


def process_path_len_data(analyze_data):
    """处理路径长度数据并生成路径长度字典"""
    path_len_dict = defaultdict(list)

    for triple_name, triple_dict in analyze_data.items():
        fun_path_info = triple_dict['fun_path_info']

        for index, path_length in enumerate(triple_dict["path_length_list"]):
            add_flag = process_path_length(path_length, fun_path_info, index)
            path_len_dict[path_length-1].append(add_flag)

    return path_len_dict


def process_path_length(path_length, fun_path_info, index):
    """处理单个路径长度的标记计算"""
    add_flag = 0  # 默认标记为0

    if len(fun_path_info[str(index)]) != path_length - 1:
        add_flag = len(fun_path_info[str(index)]) - 1
    elif add_flag == 0:
        for duplet_dict in fun_path_info[str(index)].values():
            if duplet_dict.get("path_num_list", []):
                add_flag += 1
            else:
                break

    return add_flag


def generate_path_len_list(path_len_dict):
    """根据路径长度字典生成路径长度列表"""
    _path_len_dict = {}

    for path_length, values in path_len_dict.items():
        if path_length > 10:
            continue
        value_counts = defaultdict(int)
        for value in values:
            value_counts[value] += 1

        total = len(values)
        _path_len_dict[path_length] = {key: count / total for key, count in value_counts.items()}

    return _path_len_dict


def plot_path_length_distribution(path_len_dict, min_threshold=0.01):
    """绘制路径长度与标记比例的堆叠条形图
       显示从0到0.7的部分数据，y轴从0.75开始显示，辅助显示0-0.75的数据，
       并标注每个堆叠区域的百分比。
    """

    # 获取所有路径长度，并按升序排序
    path_lengths = sorted(path_len_dict.keys())

    # 获取所有标记（例如 "0", "1", "2" 等）
    flag_all_proportions = set([x for _, value in path_len_dict.items() for x in value.keys() if int(x) < 4])

    # 初始化堆叠条形图的底部数据
    bottom = [0] * len(path_lengths)

    # 创建堆叠条形图
    fig, ax = plt.subplots(figsize=(10, 8))

    # 绘制从 0 到 0.7 的透明辅助条形图
    for flag in flag_all_proportions:
        # 获取每个路径长度中该标记的比例
        proportions = [path_len_dict[path_length].get(flag, 0) for path_length in path_lengths]

        # 计算每个比例在0到0.7部分的展示
        proportions_below_0_75 = [p if p < 0.75 else 0 for p in proportions]

        # 绘制0到0.75的透明区域（辅助部分）
        ax.bar(path_lengths, proportions_below_0_75, bottom=bottom, color='lightgray', edgecolor='black', alpha=0.5)

    # 重新初始化底部数据
    bottom = [0] * len(path_lengths)

    # 为每个标记绘制堆叠条形图
    for flag in flag_all_proportions:
        # 获取每个路径长度中该标记的比例
        proportions = [path_len_dict[path_length].get(flag, 0) for path_length in path_lengths]

        # 绘制堆叠条形图
        ax.bar(path_lengths, proportions, bottom=bottom, label=f"{flag}", edgecolor='black', alpha=0.7)

        # 添加百分比标注
        for i, path_length in enumerate(path_lengths):

            proportion = proportions[i]

            # 计算该部分的百分比
            total_height = sum([path_len_dict[path_length].get(f, 0) for f in flag_all_proportions])
            percent = (proportion / total_height) * 100
            if percent < 0.7:
                continue

            if bottom[i] == 0:
                y_loc = proportion / 2 + 0.75 / 2
            else:
                y_loc = bottom[i] + proportion / 2

            ax.text(path_length, y_loc, f'{percent:.2f}%', ha='center', va='center', fontsize=10,
                    color='black')

        # 更新底部数据，以便下一个标记能够堆叠在其上
        bottom = [bottom[i] + proportions[i] for i in range(len(bottom))]

    # 设置图表标题与标签
    ax.set_xlabel('Path Length', fontsize=14)
    ax.set_ylabel('Proportion', fontsize=14)

    ax.set_ylim(0.75, 1)  # y轴从 0 到 1，但在显示时展示为0.75至1

    # 显示图例，避免重叠
    # plt.subplots_adjust(right=0.85)
    # ax.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Reached Length")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, title="Reached Length")
    # 自动调整布局
    plt.tight_layout()

    # 保存图表
    plt.savefig("path_length_distribution.png", bbox_inches='tight', dpi=900)
    plt.show()

def print_anlyze_res(path_len_dict):
    all_list = []
    for path_length, values in path_len_dict.items():

        all_list.extend(values)
    print("所有依赖路径为",len(all_list))




def main():
    """主函数，调用加载数据、处理数据、绘制图表"""
    try:
        # 加载数据
        analyze_data = load_analyze_data('data.pkl')

        # 处理路径长度数据
        path_len_dict = process_path_len_data(analyze_data)

        print_anlyze_res(path_len_dict)

        # 生成路径长度列表（包括比例）
        path_len_dict = generate_path_len_list(path_len_dict)

        # 输出结果
        print(json.dumps(path_len_dict, indent=4))

        # 绘制路径长度分布图
        plot_path_length_distribution(path_len_dict)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
