import json
import matplotlib.pyplot as plt
import numpy as np

import pickle



def load_analyze_data(filepath):
    """加载分析数据"""
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def process_path_num_data(analyze_data):
    """处理路径长度数据并生成路径长度列表"""
    path_len_dict = {}


    # 遍历所有triple_name数据
    for triple_name in analyze_data:
        triple_dict = analyze_data[triple_name]
        path_num = len(triple_dict['path_length_list'])
        if path_num > 13:
            continue
        is_reachable =triple_dict["is_reachable"] # is_reachable是布尔值，可达为True
        if path_num not in path_len_dict:
            path_len_dict[path_num] = []

        path_len_dict[path_num].append(is_reachable)

    return path_len_dict


def generate_path_len_list(path_len_dict):
    """根据路径数量字典生成路径长度列表

    返回结构：
    [
        [路径数量, 不可达数量, 可达数量, 可达率],
        ...
    ]
    """

    result = []

    for path_num, reachable_flags in path_len_dict.items():
        # 可达为 True，记作 1，不可达为 False，记作 0
        reachable_count = sum(1 for x in reachable_flags if x)
        unreachable_count = len(reachable_flags) - reachable_count
        total = len(reachable_flags)

        if total == 0:
            reachable_ratio = 0
        else:
            reachable_ratio = reachable_count / total

        result.append([path_num, unreachable_count, reachable_count, reachable_ratio])

    return result


def plot_path_len(path_len_dict):
    """绘制路径数量与可达率的条形图 + 样本数量（右轴，单位为k）"""

    data = generate_path_len_list(path_len_dict)
    data.sort(key=lambda x: x[0])

    path_nums = [x[0] for x in data]
    unreachable_counts = [x[1] for x in data]
    reachable_counts = [x[2] for x in data]
    reachable_ratios = [x[3] for x in data]
    total_counts = [un + r for un, r in zip(unreachable_counts, reachable_counts)]

    fig, ax1 = plt.subplots(figsize=(6, 4), dpi=600)

    # 网格线 + 背景虚线参考线
    ax1.grid(axis='x', alpha=0.4)
    ax1.grid(axis='y', alpha=0.4)
    for i in range(1, 10, 2):
        ax1.axhline(i * 0.02, linestyle='--', color="#CBCBCB", alpha=0.3, linewidth=1)

    # 柱状图：可达率
    bars = ax1.bar(
        path_nums,
        reachable_ratios,
        color='steelblue',
        edgecolor='black',
        alpha=0.8,
        label='Reachability Ratio'
    )

    # 左侧 Y 轴设置
    ax1.set_ylabel('Reachability Ratio (%)', fontsize=20, labelpad=10)
    ax1.set_xlabel('Number of Paths', fontsize=20, labelpad=10)
    ax1.set_ylim(0, 0.2)
    ax1.set_xticks(path_nums)
    ax1.set_xticklabels(path_nums, fontsize=16, rotation=30)
    ax1.set_yticks(np.linspace(0, 0.2, 5))
    ax1.set_yticklabels([f'{int(y * 100)}%' for y in np.linspace(0, 0.2, 5)], fontsize=16)

    # 柱顶标注（比例 > 0.01）
    num =0
    for rect, ratio in zip(bars, reachable_ratios):
        num+=1
        if num%2 == 0:
            continue
        height = rect.get_height()
        if height > 0.01:
            ax1.text(
                rect.get_x() + rect.get_width() / 2,
                height + 0.005,
                f'{ratio * 100:.1f}%',
                ha='center',
                va='bottom',
                fontsize=10
            )

    # 右侧 Y 轴：样本数量
    ax2 = ax1.twinx()
    ax2.plot(
        path_nums,
        total_counts,
        color='green',
        marker='o',
        linestyle='--',
        linewidth=2,
        # label='Sample Count'
    )
    # ax2.set_ylabel('Sample Count (k)', fontsize=20, color='green', labelpad=10)
    ax2.tick_params(axis='y', labelsize=16, labelcolor='green')

    # 设置右轴刻度为 k
    y_max = max(total_counts)
    y_ticks = np.linspace(0, y_max * 1.2, 5)
    ax2.set_yticks(y_ticks)
    ax2.set_yticklabels([f'{y / 1000:.1f}k' for y in y_ticks], fontsize=16)

    # 折线图标注
    for i, count in enumerate(total_counts):
        if i!=0:
            continue
        ax2.text(
            path_nums[i],
            count + y_max * 0.05,
            f'{count / 1000:.1f}k',
            ha='center',
            va='bottom',
            fontsize=10,
            color='green'
        )

    # 合并图例并统一居中放在图底部
    # handles1, labels1 = ax1.get_legend_handles_labels()
    # handles2, labels2 = ax2.get_legend_handles_labels()
    # ax1.legend(handles1 + handles2, labels1 + labels2,
    #            loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=16)

    plt.tight_layout()
    plt.savefig("path_count_vs_reachability.png", dpi=800, bbox_inches='tight')
    plt.show()
    plt.close()
def main():
    """主函数，调用加载数据、处理数据、绘制图表"""
    try:
        analyze_data = load_analyze_data('data.pkl')
        path_len_dict = process_path_num_data(analyze_data)
        plot_path_len(path_len_dict)
    except FileNotFoundError:
        print("Error: The file was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from the file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()
