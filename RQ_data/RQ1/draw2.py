import json
import os
import numpy as np
import matplotlib.pyplot as plt


# 加载分析数据
import pickle

# # 加载数据
# with open(r'data.pkl', 'rb') as f:
#     analyze_data = pickle.load(f)


# 计算图中所有边的数量
def get_edges_num(dependencies):
    return sum(len(neighbors) for neighbors in dependencies.values())


# 提取无向图中的所有边
def extract_edges(graph):
    edges = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            edges.add(frozenset([node, neighbor]))
    return edges


# 获取两个图之间的不同边的数量
def get_diff_edges_num(graph1, graph2):
    edges_1 = extract_edges(graph1)
    edges_2 = extract_edges(graph2)
    return len(edges_1 - edges_2), len(edges_2 - edges_1)


# 计算LDR和RDR，并根据包名分组
def compute_LDR_RDR(analyze_data):
    ratio_dict = {}
    LDR_dict, RDR_dict = {}, {}

    for depen_name, depen_dict in analyze_data.items():
        # 获取依赖信息
        E_D_num = get_edges_num(depen_dict.get('original_dependency', {}))
        E_R_num = get_edges_num(depen_dict.get('all_dependency', {}))

        # 计算LD和RD
        LD_edge_num, RD_edge_num = get_diff_edges_num(depen_dict['all_dependency'], depen_dict['original_dependency'])
        LDR = LD_edge_num / E_R_num if E_R_num else 0
        RDR = RD_edge_num / E_D_num if E_D_num else 0

        # 计算平均LDR和RDR
        package_name = depen_name.split('@')[2]
        ratio_dict[depen_name] = [LDR, RDR, E_R_num, E_D_num]

        if package_name not in LDR_dict:
            LDR_dict[package_name], RDR_dict[package_name] = [], []
        LDR_dict[package_name].append(LDR)
        RDR_dict[package_name].append(RDR)

    # 计算每个包的平均LDR和RDR
    for package_name in LDR_dict:
        LDR_dict[package_name] = np.mean(LDR_dict[package_name])
        RDR_dict[package_name] = np.mean(RDR_dict[package_name])

    return ratio_dict, LDR_dict, RDR_dict


# 计算下载数据
def load_downloads_data(downloads_dir, com_set):
    downloads_dict = {}
    for json_file in os.listdir(downloads_dir):
        with open(os.path.join(downloads_dir, json_file), 'r') as f:
            data = json.load(f)
        for com_dict in data:
            if com_dict['package_name'] in com_set:
                downloads_dict[com_dict['package_name']] = downloads_dict.get(com_dict['package_name'], 0) + int(com_dict['num_downloads'])
    return downloads_dict


# 绘制散点图和多项式拟合曲线
def plot_scatter_with_fit(x, y, xlabel='', ylabel='', title='', save_path='', label=""):
    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure(figsize=(6, 4), dpi=600)

    # 散点图
    plt.scatter(
        x, y,
        color='lightblue',
        edgecolors='k',
        alpha=0.7,
        label=f'Avg. {label}'
    )

    # 多项式拟合
    degree = 3
    coefficients = np.polyfit(x, y, degree)
    x_fit = np.linspace(np.min(x), np.max(x), 200)
    y_fit = np.polyval(coefficients, x_fit)

    plt.plot(
        x_fit, y_fit,
        color='red',
        linestyle='-',
        linewidth=2,
        label=f'{label} Trend'
    )

    # 标题和坐标轴标签
    plt.title(title, fontsize=24, fontweight='bold')
    plt.xlabel(xlabel if xlabel else 'Download Count (k)', fontsize=24)
    plt.ylabel(ylabel if ylabel else label, fontsize=24)

    # 网格
    plt.grid(axis='both', alpha=0.4)

    # 获取当前 x 轴刻度
    xticks = plt.xticks()[0]
    xticks = [val for val in xticks if val >= 0]  # 仅保留非负刻度

    # 格式化标签（两位小数 + k 单位）
    xtick_labels = [f'{val / 1000:.1f}k' for val in xticks]
    plt.xticks(ticks=xticks, labels=xtick_labels, fontsize=18, rotation=30)

    # y 轴刻度
    plt.yticks(fontsize=18)

    # 图例（缩小字号）
    plt.legend(loc='best', fontsize=18)

    # 保存图像
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()
    plt.close()


# 主流程
def main():
    import pickle

    # 加载数据
    with open(r'data.pkl', 'rb') as f:
        analyze_data = pickle.load(f)

    # 计算LDR和RDR
    ratio_dict, LDR_dict, RDR_dict = compute_LDR_RDR(analyze_data)

    # 获取com_set（包名集合）
    com_set = {depen_name.split('@')[2] for depen_name in analyze_data}

    # 计算下载数据
    downloads_dict = load_downloads_data("downloads_data", com_set)

    # 根据下载数排序
    dep_list = sorted([[key, value] for key, value in downloads_dict.items()], key=lambda x: x[1])

    # 准备绘制数据
    plt_list = []
    for dep_name, download_count in dep_list:
        if dep_name in LDR_dict:
            plt_list.append([int(download_count), float(LDR_dict[dep_name]), float(RDR_dict[dep_name])])

    plt_list = np.array(plt_list)

    interval_step = 100
    # 分割数据
    sub_matrices = {i: plt_list[i:i + interval_step] for i in range(0, len(plt_list), interval_step)}

    # 计算每个子矩阵的平均LDR和RDR
    plt_atrices = [[int(i), np.mean(sub[:, 1]), np.mean(sub[:, 2])] for i, sub in sub_matrices.items()]

    plt_atrices = np.array(plt_atrices)

    # 绘制LDR与下载数的散点图并拟合
    x = np.arange(len(plt_atrices)) * interval_step
    # Relationship Between Popularity and Average LDR
    plot_scatter_with_fit(x, plt_atrices[:, 1], xlabel='Monthly Download Count', ylabel='LDR',
                          title='',
                          save_path='./Relationship_Between_LDR_and_DownloadCount.png',
                          label="LDR")

    # 绘制RDR与下载数的散点图并拟合
    # Relationship Between Popularity and Average RDR
    plot_scatter_with_fit(x, plt_atrices[:, 2], xlabel='Monthly Download Count', ylabel='RDR',
                          title='',
                          save_path='./Relationship_Between_RDR_and_DownloadCount.png',
                          label="RDR")


if __name__ == "__main__":
    main()
