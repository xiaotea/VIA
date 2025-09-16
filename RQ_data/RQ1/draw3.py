import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

# 加载数据的函数
def load_data(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def load_csv_data(filepath):
    """ 直接使用 pandas 读取 CSV 数据 """
    return pd.read_csv(filepath, header=None)  # 如果有头部信息可以设置 header=0


# 常量定义
CSV_DATA_PATH = r'Triad.csv'
CTX_DATA_PATH = r'data.pkl'

# 加载数据
analyze_data = load_data(CTX_DATA_PATH)  # 加载 JSON 数据
analyze_data_list = load_csv_data(CSV_DATA_PATH)  # 加载 CSV 数据

reachable_cve_num = 0
all_cve_num = len(analyze_data_list)  # CVE 总数

new_analyze_data_list = []

# 遍历并处理数据
for row in analyze_data_list.itertuples(index=False, name=None):
    _com_name = row[1] + '@' + row[2]  # 创建组件名称
    if _com_name not in analyze_data:  # 检查组件是否在分析数据中
        continue

    reachable_paths = analyze_data[_com_name].get("deploy_paths", [])
    reachable = "True" if reachable_paths else "False"  # 判断是否有可达路径

    new_row = list(row)  # 将当前行转换为列表（可以修改）
    new_row.extend([reachable, reachable_paths])  # 添加 "True"/"False" 和路径

    new_analyze_data_list.append(new_row)  # 将新行加入到结果列表

    all_cve_num += 1
    if reachable == "True":
        reachable_cve_num += 1  # 增加可达 CVE 的计数

# 输出统计信息
print(f'漏洞能够影响到组件的有：{reachable_cve_num} / {all_cve_num} = {reachable_cve_num / all_cve_num:.4f}')

# 将新的数据保存到 DataFrame
df_new_analyze_data_list = pd.DataFrame(new_analyze_data_list)


# 保存到 CSV 文件
# df_new_analyze_data_list.to_csv("result_csv.csv", index=False, header=False)

# 绘制散点图并进行多项式拟合
def plot_scatter_with_fit(x, y, xlabel='', ylabel='', title='', save_path=None, label=""):
    """
    绘制散点图并添加多项式拟合曲线

    Parameters:
    x (array-like): x轴数据
    y (array-like): y轴数据
    xlabel (str): x轴标签
    ylabel (str): y轴标签
    title (str): 图表标题
    save_path (str, optional): 图表保存路径（默认为 None，不保存）
    """
    plt.figure(figsize=(6, 5))
    plt.scatter(x, y, color='steelblue', edgecolors='black', alpha=0.7, s=40)

    # 多项式拟合
    degree = 4  # 拟合阶数
    coefficients = np.polyfit(x, y, degree)
    x_fit = np.linspace(np.min(x), np.max(x), 100)
    y_fit = np.polyval(coefficients, x_fit)
    plt.plot(x_fit, y_fit, color='red', linestyle='-', linewidth=2, label=label)

    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    # 设置标题和标签
    plt.title(title, fontsize=20, fontweight='bold')
    plt.xlabel(xlabel, fontsize=18)
    plt.ylabel(ylabel, fontsize=18)

    # 设置图例和网格
    plt.legend(loc='best', fontsize=18)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # 自动调整布局
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=800, bbox_inches='tight')

    plt.show()
    plt.close()


# 路径统计
reachable_path_num = 0
original_path_num = 0
path_num_reachable_dict = {}
path_len_reachable_dict = {}
shortest_path_len_dict = {}
# shortest_three_path_len_dict = {}

for com_dependency in analyze_data:
    reachable_paths = analyze_data[com_dependency]["deploy_paths"]
    original_path = analyze_data[com_dependency]["original_path"]
    original_path_num += 1

    path_num = len(original_path)
    is_reachable = bool(reachable_paths)
    if path_num not in path_num_reachable_dict:
        path_num_reachable_dict[path_num] = []
        shortest_path_len_dict[path_num] = []

    path_num_reachable_dict[path_num].append(is_reachable)
    shortest_path_len_dict[path_num].extend([len(path) for path in original_path][:1])

    if is_reachable:
        reachable_path_num += 1

# 输出可达路径占比
print("可达依赖路径占比为：", reachable_path_num / original_path_num, reachable_path_num, original_path_num)

# 统计路径长度与可达比率
path_num_list = []
for path_num in path_num_reachable_dict:
    if path_num > 80:
        continue

    bool_list = path_num_reachable_dict[path_num]
    ratio = sum(bool_list) / len(bool_list) if bool_list else 0
    shortest_path_len_list = shortest_path_len_dict.get(path_num, [])
    avg_shortest_path_len = np.mean(shortest_path_len_list) if shortest_path_len_list else 0

    path_num_list.append([path_num, ratio, avg_shortest_path_len])

# 转换为 NumPy 数组
path_num_list = np.array(path_num_list)
print(path_num_list)

# 绘制路径数与可达比率图
plot_scatter_with_fit(
    path_num_list[:, 0], path_num_list[:, 1], xlabel='Path Number', ylabel='Reachable Ratio',
    # title='Path Number vs Reachable Ratio',
    save_path='Path-Number-vs-Reachable-Ratio',
    label="Reachable Ratio Trend"

)

# 绘制路径数与最短路径长度图
plot_scatter_with_fit(
    path_num_list[:, 0], path_num_list[:, 2], xlabel='Path Number', ylabel='Shortest Path Length',
    # title='Path Number vs Shortest Path Length',
    save_path='Path-Number-vs-Shortest-Path-Length',
    label="Shortest Path Trend"
)
