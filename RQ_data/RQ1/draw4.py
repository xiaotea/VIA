import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

# 加载数据的函数：从 JSON 文件中读取数据
def load_json_data(filepath):
    """从指定路径加载 JSON 数据"""
    with open(filepath, 'rb') as file:
        return pickle.load(file)


# 加载 CSV 数据的函数：直接使用 pandas 读取 CSV 文件
def load_csv_data(filepath):
    """从指定路径加载 CSV 数据"""
    return pd.read_csv(filepath, header=None)  # header=None 表示没有标题行


# 绘制条形图并进行多项式拟合
def plot_bar_with_fit(x, y, percent_x, percent_y, xlabel='', ylabel='', title='', save_path=None):
    """
    绘制条形图并添加多项式拟合曲线和百分比折线图，使用统一的 y 轴。

    Parameters:
    x (array-like): x轴数据
    y (array-like): y轴数据
    percent_x (array-like): 百分比折线图的 x 数据
    percent_y (array-like): 百分比折线图的 y 数据
    xlabel (str): x轴标签
    ylabel (str): y轴标签
    title (str): 图表标题
    save_path (str, optional): 图表保存路径（默认为 None，不保存）
    """
    fig, ax1 = plt.subplots(figsize=(6, 5))

    # 绘制条形图
    bar_width = 0.6  # 设置条形宽度
    bars = ax1.bar(x, y, width=bar_width, color='lightblue', edgecolor='k', alpha=0.7, align='center')

    # 在条形图上标上百分比数值
    for i, bar in enumerate(bars):
        if i not in  [0, 1, 2, 3,4,5,7,9]:
            continue  # 只标这几个
        height = bar.get_height()
        percentage = f'{height * 100:.1f}%'
        ax1.text(bar.get_x() + bar.get_width() / 2, height + 0.02, percentage, ha='center', va='bottom', fontsize=14)

    # 多项式拟合
    degree = 6 # 设置拟合多项式的阶数
    coefficients = np.polyfit(x, y, degree)  # 计算多项式的系数
    x_fit = np.linspace(np.min(x), np.max(x), 100)  # 为拟合曲线生成更平滑的x值
    y_fit = np.polyval(coefficients, x_fit)  # 计算对应的y值
    x_fit = [x for x in x_fit if x <= 7]
    y_fit = y_fit[:len(x_fit)]
    # 绘制拟合曲线
    # ax1.plot(x_fit, y_fit, color='red', linestyle='-', linewidth=2, label='Polynomial Fit')
    ax1.plot(x_fit, y_fit, color='red', linestyle='-', linewidth=2)
    # 设置标题和标签
    ax1.set_xlabel(xlabel, fontsize=22)
    ax1.set_ylabel(ylabel, fontsize=22)
    # ax1.set_title(title, fontsize=22, fontweight='bold')
    # 设置 y 轴范围，使两个图形使用统一的 y 轴
    ax1.set_ylim(0, 1.1)  # 设置y轴范围 [0, 1] 以适应条形图和百分比线

    # 显示网格
    ax1.grid(True)

    # 设置字体和图例
    ax1.legend(loc='best', fontsize=12)

    # 在同一个图上绘制百分比折线图
    ax2 = ax1.twinx()
    # ax2.plot(percent_x, percent_y, color='green', marker='o', linestyle='-', linewidth=2,
    #          label='Cumulative Percentage', alpha=0.7)
    #

    ax2.plot(percent_x, percent_y, color='green', marker='o', linestyle='-', linewidth=2, alpha=0.7)

    # 设置百分比折线图的 y 轴标签
    ax2.set_ylabel('Cumulative Percentage (%)', fontsize=22, color='green')
    ax2.legend(loc='upper left', fontsize=12)

    # 设置百分比文本标签（舍去小数点后两位数字）
    # 折线图数值标签，偏移更大避免重叠
    for i, p in enumerate(percent_y):
        if i not in [0, 1, 2, 4]:
            continue
        percentage = f'{int(p * 1000) / 10:.1f}%'
        y_offset = 0.04
        ax2.text(percent_x[i], p + y_offset, percentage, color='green', ha='center', va='bottom', fontsize=12)
        if p == 1:
            break

    ax2.set_ylim(0, 1.1)

    # 自动调整布局
    plt.tight_layout()


    # 可选：保存图表
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=900)
    # else:
        # 显示图表
    plt.show()

    plt.close()


# 加载数据路径
CSV_DATA_PATH = r'Triad.csv'
CTX_DATA_PATH = r'data.pkl'

# 加载 JSON 和 CSV 数据
analyze_data = load_json_data(CTX_DATA_PATH)  # 加载 JSON 数据
analyze_data_list = load_csv_data(CSV_DATA_PATH)  # 加载 CSV 数据

# 初始化统计变量
reachable_path_count = 0  # 可达路径数量
path_len_reachable_dict = {}  # 存储路径长度与可达路径的关系

path_count, LD_path_count, completely_LD_path_count = 0, 0, 0
LDpath_num, LD_allnum = 0, 0
two_len_path_count = 0

reached_shortest_path_list = []

# 遍历每个组件的依赖数据
for component in analyze_data:
    reachable_paths = analyze_data[component].get("deploy_paths", [])  # 获取组件的可达路径
    original_paths = analyze_data[component].get("original_path", [])  # 获取组件的原始路径

    original_path_set = set(["@".join(path) for path in original_paths])  # 将原始路径转为集合，便于查找

    # 计算隐式依赖关系对于可达率的影响
    reachable_path_set = set(["@".join(path) for path in reachable_paths])

    if len(reachable_path_set) != 0:
        if len(original_paths) == 1 and len(original_paths[0]) == 2:
            two_len_path_count += 1
        # 若是可达的路径完全在原路径中，则不存在隐式路径
        if len(reachable_path_set - original_path_set) == 0:
            path_count += 1
        # 部分可达的路径不在原路径中
        elif len(reachable_path_set - original_path_set) > 0:
            LD_allnum = LD_allnum + len(reachable_path_set)
            LDpath_num = LDpath_num + len(reachable_path_set - original_path_set)
            LD_path_count += 1
        # 所有可达的路径不在原路径中
        if len(reachable_path_set - original_path_set) == len(reachable_path_set):
            completely_LD_path_count += 1

    shortest_path = 10000
    # 遍历可达路径并计算路径长度
    for path in reachable_paths:

        path_length = len(path)  # 计算当前路径的长度

        path_str = '@'.join(path)  # 将路径转换为字符串形式

        if path_length not in path_len_reachable_dict:
            path_len_reachable_dict[path_length] = []

        # 如果该路径是原始路径的一部分，标记为可达
        is_reachable = path_str in original_path_set
        if path_length < shortest_path:
            shortest_path = path_length
        path_len_reachable_dict[path_length].append(is_reachable)
    if shortest_path != 10000:
        reached_shortest_path_list.append(shortest_path)

percent_list = []
percent_num = 0.0
for path_length in range(2, 11):
    print(percent_num)
    num_len = len([x for x in reached_shortest_path_list if x == path_length])
    percent_num = percent_num + num_len / len(reached_shortest_path_list)
    print([path_length, percent_num])
    percent_list.append([path_length, percent_num])

print(path_count, LD_path_count, completely_LD_path_count, LD_allnum, LDpath_num, LDpath_num / LD_allnum)

print("完全没有隐式依赖路径的组件", path_count)
print("包含隐式依赖路径的组件", LD_path_count)
print("完全由隐式依赖路径组成的组件", completely_LD_path_count)
print("统计所有隐式依赖路径的总数量", LD_allnum)
print("统计所有可达路径的总数量", LDpath_num)
print("隐式依赖的“覆盖度”", LDpath_num / LD_allnum)
print("可达的二元组依赖路径长度大于2", two_len_path_count)

# 计算每个路径长度的可达比率
path_length_ratio_list = []
for path_length, reachable_flags in path_len_reachable_dict.items():
    if path_length > 14:
        continue
    reachable_ratio = sum(reachable_flags) / len(reachable_flags) if reachable_flags else 0
    path_length_ratio_list.append([path_length, reachable_ratio])

# 将路径长度和可达比率转为 NumPy 数组，方便绘图
path_length_ratio_array = np.array(path_length_ratio_list)

# 打印路径长度与可达比率数据
# print("路径长度与可达比率数据：")
# print(path_length_ratio_array)
# print(percent_list)

# 绘制路径长度与可达比率的条形图和拟合曲线
plot_bar_with_fit(
    path_length_ratio_array[:, 0],  # 路径长度
    path_length_ratio_array[:, 1],  # 可达比率
    np.array([x[0] for x in percent_list]),
    np.array([x[1] for x in percent_list]),
    xlabel='Path Length',  # x轴标签
    ylabel='Reachable Ratio',  # y轴标签
    # title='Path Length vs Reachable Ratio',  # 图表标题
    save_path='Path-Length-vs-Reachable-Ratio'  # 如果需要保存图表，请提供路径
)
