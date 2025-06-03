import json
import pickle

import numpy as np
import matplotlib.pyplot as plt

import pickle

# 加载数据
with open(r'data.pkl', 'rb') as f:
    analyze_data = pickle.load(f)


# 辅助函数
def get_edges_num(dependencies):
    """计算图中所有边的数量"""
    return sum(len(neighbors) for neighbors in dependencies.values())


def extract_edges(graph):
    """提取图中所有的边"""
    return {frozenset([node, neighbor]) for node, neighbors in graph.items() for neighbor in neighbors}


def get_diff_edges_num(graph1, graph2):
    """计算两个图之间不同边的数量"""
    edges_1, edges_2 = extract_edges(graph1), extract_edges(graph2)
    return len(edges_1 - edges_2), len(edges_2 - edges_1)


def compute_statistics(analyze_data):
    """计算LDR和RDR，并返回相关统计信息"""
    ratio_dict = {}
    num1, num2, num3, num4 = 0, 0, 0, 0
    eve_LDR, eve_RDR = 0, 0

    for depen_name, depen_dict in analyze_data.items():
        num1 += 1
        E_D_num = get_edges_num(depen_dict.get('original_dependency', {}))
        E_R_num = get_edges_num(depen_dict.get('deploy_dependency', {}))

        LD_edge_num, RD_edge_num = get_diff_edges_num(depen_dict.get('deploy_dependency', {}),
                                                      depen_dict.get('original_dependency', {}))
        LDR = LD_edge_num / E_R_num if E_R_num > 0 else 0.0
        RDR = RD_edge_num / E_D_num if E_D_num > 0 else 0.0

        if LDR > 0.2 and len(depen_dict.get('original_path', [])) < 3 and not "-" in depen_name:
            print(depen_name)
            print(depen_dict)
            print("=====================")

        eve_LDR += LDR
        eve_RDR += RDR

        # 统计LDR、RDR为零的情况
        num2 += (LDR == 0 and RDR == 0)
        num3 += (LDR == 0)
        num4 += (RDR == 0)

        # 存储每个包的LDR, RDR和边的数量
        ratio_dict[depen_name] = [LDR, RDR, E_R_num, E_D_num]

    return ratio_dict, num1, num2, num3, num4, eve_LDR, eve_RDR


def print_statistics(num1, num2, num3, num4, eve_LDR, eve_RDR):
    """打印统计结果"""
    print(f"所有的二元组数目: {num1}")
    print(f"依赖关系存在隐性的二元组: {1 - num3 / num1:.4f}")
    print(f"依赖关系冗余的二元组: {1 - num4 / num1:.4f}")
    print(f"依赖关系不正确的二元组: {1 - num2 / num1:.4f}")
    print(f"依赖关系隐性率: {eve_LDR / num1:.4f}")
    print(f"依赖关系冗余率: {eve_RDR / num1:.4f}")
    print(f"依赖关系不正确率: {(eve_LDR + eve_RDR) / (2 * num1):.4f}")


def prepare_data_for_plot(ratio_dict):
    """构建矩阵并进行排序"""
    matrix = np.array([ratio_dict[x] for x in ratio_dict])
    sorted_matrix = matrix[matrix[:, 3].argsort()]

    # 根据唯一值分割矩阵
    sub_matrices = {value: sorted_matrix[sorted_matrix[:, 3] == value] for value in np.unique(sorted_matrix[:, 3])}

    # 提取绘图数据
    plt_atrices = [
        [x, np.mean(sub_matrices[x][:, 0]), np.mean(sub_matrices[x][:, 1])]
        for x in sub_matrices if x <= 200
    ]
    return np.array(plt_atrices)


def plot_relationship(x_data, y_data, y_label, filename, degree=3.5, label1="", label2=""):
    """绘制散点图并进行多项式拟合（带辅助线和网格）"""
    x = np.arange(len(y_data))
    fig, ax = plt.subplots(figsize=(6, 4), dpi=600)

    # 网格线
    ax.grid(axis='x', alpha=0.4)
    ax.grid(axis='y', alpha=0.4)

    # 水平参考线（虚线）
    for i in range(1, 10, 2):  # 每隔 0.2 添加一条线
        ax.axhline(i * 0.1, linestyle='--', color="#CBCBCB", alpha=0.3, linewidth=1)

    # 散点图
    ax.scatter(x, y_data, label=label1, color='lightblue', edgecolors='k', s=20, alpha=1.0, zorder=10)

    # 拟合曲线
    coefficients = np.polyfit(x, y_data, degree)
    x_fit = np.linspace(np.min(x), np.max(x), 200)
    y_fit = np.polyval(coefficients, x_fit)
    ax.plot(x_fit, y_fit, color='red', linestyle='-', linewidth=2, label=label2, zorder=11)

    # 坐标标签
    ax.set_xlabel('Edge Count', fontsize=20, labelpad=10)
    ax.set_ylabel(y_label, fontsize=20, labelpad=10)

    # 动态设置刻度标签
    tick_step = max(len(x_data) // 6, 1)
    tick_positions = np.arange(0, len(x), tick_step)
    tick_labels = [f'{x_data[i]:.0f}' for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=16, rotation=30)
    ax.tick_params(axis='y', labelsize=16)

    # 图例
    ax.legend(loc='best', fontsize=16)

    # 保存
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=800)
    plt.show()
    plt.close()


# 主要流程
ratio_dict, num1, num2, num3, num4, eve_LDR, eve_RDR = compute_statistics(analyze_data)

# 打印统计信息
print_statistics(num1, num2, num3, num4, eve_LDR, eve_RDR)

# 准备绘图数据
plt_atrices = prepare_data_for_plot(ratio_dict)

# 绘制LDR与边数关系图
plot_relationship(plt_atrices[:, 0], plt_atrices[:, 1], 'LDR',
                  './Relationship_Between_LDR_and_Edge_Number.png',
                  label1='Average. LDR',
                  label2='LDR Trend')

# 绘制RDR与边数关系图
plot_relationship(plt_atrices[:, 0], plt_atrices[:, 2], 'RDR',
                  './Relationship_Between_RDR_and_Edge_Number.png',
                  label1='Average. RDR',
                  label2='RDR Trend')
