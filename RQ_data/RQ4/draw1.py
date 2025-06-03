import json
import matplotlib.pyplot as plt
import numpy as np
import pickle

def load_analyze_data(filepath):
    """加载分析数据"""
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def process_path_len_data(analyze_data):
    """处理路径长度数据并生成路径长度列表"""
    path_len_dict = {}


    # 遍历所有triple_name数据
    for triple_name in analyze_data:
        triple_dict = analyze_data[triple_name]
        fun_path_info = triple_dict['fun_path_info']

        # 遍历路径长度列表
        for index, path_length in enumerate(triple_dict["path_length_list"]):

            if path_length>7:
                continue
            if path_length not in path_len_dict:
                path_len_dict[path_length] = []

            add_flag = 1  # 默认标记为1

            # 检查路径长度和fun_path_info的匹配情况
            if len(fun_path_info[str(index)]) != path_length - 1:
                add_flag = 0  # 若不匹配，则标记为0
                path_len_dict[path_length].append(add_flag)
                continue

            # 检查路径数量是否符合要求
            for duplet, duplet_dict in fun_path_info[str(index)].items():
                if len(duplet_dict.get("path_num_list", [])) == 0:
                    add_flag = 0  # 若路径数量为空，则标记为0
                    break
            path_len_dict[path_length].append(add_flag)

    return path_len_dict


def generate_path_len_list(path_len_dict):
    """根据路径长度字典生成路径长度列表"""
    return [
        [key, value.count(0), value.count(1), value.count(1) / len(value)]
        for key, value in path_len_dict.items()
    ]


def plot_path_len(path_len_dict):
    """绘制路径数量与可达率的条形图 + 样本数量（k为单位）"""

    data = generate_path_len_list(path_len_dict)
    data.sort(key=lambda x: x[0])

    path_nums = [x[0] for x in data]
    unreachable_counts = [x[1] for x in data]
    reachable_counts = [x[2] for x in data]
    reachable_ratios = [x[3] for x in data]
    total_counts = [un + r for un, r in zip(unreachable_counts, reachable_counts)]

    fig, ax1 = plt.subplots(figsize=(6, 4), dpi=600)

    # 柱状图：可达率
    bar = ax1.bar(
        path_nums,
        reachable_ratios,
        color='steelblue',
        edgecolor='black',
        alpha=0.8,
        label='Reachability Ratio'
    )

    # 左 Y 轴设置
    ax1.set_ylabel('Reachability Ratio (%)', fontsize=20)
    ax1.set_xlabel('Length of Path', fontsize=20)
    ax1.set_ylim(0, 0.2)
    ax1.set_xticks(path_nums)
    ax1.set_xticklabels(path_nums, fontsize=16, rotation=30)
    ax1.set_yticks(np.linspace(0, 0.2, 5))
    ax1.set_yticklabels([f'{int(y * 100)}%' for y in np.linspace(0, 0.2, 5)], fontsize=16)

    # 柱顶标注百分比
    for rect, ratio in zip(bar, reachable_ratios):
        height = rect.get_height()
        if height > 0.0001:
            ax1.text(
                rect.get_x() + rect.get_width() / 2,
                height + 0.005,
                f'{ratio * 100:.2f}%',
                ha='center',
                va='bottom',
                fontsize=10
            )

    # 右 Y 轴：样本总数（单位 k）
    ax2 = ax1.twinx()
    ax2.plot(
        path_nums,
        total_counts,
        color='green',
        marker='o',
        linestyle='--',
        linewidth=2,
        label='Sample Count'
    )
    ax2.set_ylabel('Sample Count (k)', fontsize=20, color='green')
    ax2.tick_params(axis='y', labelcolor='green', labelsize=16)

    # 设置右 Y 轴刻度为 k
    y_max = max(total_counts)
    y_ticks = np.linspace(0, y_max * 1.2, 5)
    ax2.set_yticks(y_ticks)
    ax2.set_yticklabels([f'{y / 1000:.1f}k' for y in y_ticks], fontsize=16)

    # 样本数标注在折线上
    for i, count in enumerate(total_counts):
        ax2.text(
            path_nums[i],
            count + y_max * 0.05,
            f'{count / 1000:.1f}k',
            ha='center',
            va='bottom',
            fontsize=10,
            color='green'
        )

    # 图例（合并左右图例）
    # lines1, labels1 = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=16)

    plt.tight_layout()
    plt.savefig("path_length_vs_reachability.png", dpi=800, bbox_inches='tight')
    plt.show()
    plt.close()


def main():
    """主函数，调用加载数据、处理数据、绘制图表"""

    analyze_data = load_analyze_data('data.pkl')
    path_len_dict = process_path_len_data(analyze_data)
    plot_path_len(path_len_dict)



if __name__ == '__main__':
    main()
