import json
import matplotlib.pyplot as plt
import numpy as np
import pickle

def load_analyze_data(filepath):
    """加载分析数据"""
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def process_path_num_data(analyze_data):
    all_list = []
    for _, x in analyze_data.items():
        used_fun_num,reached_fun_num = 0,0
        if not x['fun_path_info']:
            continue
        for key, value in x['fun_path_info'].items():
            for y, _value in value.items():
                if "used_fun_num" in _value and "reached_fun_num" in _value:
                    if _value["used_fun_num"] == 0:
                        continue
                    used_fun_num += _value["used_fun_num"]
                    reached_fun_num += _value["reached_fun_num"]
        all_list.append([used_fun_num,reached_fun_num])
    return all_list

import matplotlib.pyplot as plt
import numpy as np

# plt.rcParams["font.family"] = "Times New Roman"

def plot_number_of_risky_function(number_of_risky_function):
    # Step 1: 构造分桶（1-10，>10）
    buckets = {str(i): 0 for i in range(1, 11)}
    buckets[">10"] = 0

    for number_of_risky in number_of_risky_function:
        if number_of_risky == 0:
            continue
        elif number_of_risky > 10:
            buckets[">10"] += 1
        else:
            buckets[str(number_of_risky)] += 1

    # Step 2: 构造横轴和累计比例
    x_labels = list(buckets.keys())  # ['1', ..., '10', '>10']
    values = [buckets[k] for k in x_labels]

    total = sum(values)
    cumulative_ratios = []
    cumulative = 0
    for v in values:
        cumulative += v
        cumulative_ratios.append(cumulative / total if total > 0 else 0)

    # Step 3: 画图
    plt.figure(figsize=(6, 5), dpi=600)
    ax = plt.subplot()

    ax.bar(
        x_labels,
        cumulative_ratios,
        color="gray",
        edgecolor='black',
        width=1.0,
        linewidth=1.2,
        zorder=10,
        antialiased=False
    )

    # 辅助虚线
    for i in range(8):
        ax.axhline(0.6 + i * 0.05, linestyle='--', color="lightgray", alpha=0.3)

    # 样式设置
    ax.grid(axis="y", alpha=0.4, linewidth=1.2)
    ax.set_xlabel("Used Vulnerable APIs", fontsize=24)
    ax.set_ylabel("Ratio of Triples", fontsize=24)
    ax.set_ylim(0.3, 1.05)
    ax.set_xticks(range(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=30, ha='right', fontsize=22)
    ax.tick_params(axis='both', labelsize=22)

    plt.tight_layout()
    plt.savefig("./RISKY_FUNCTION_COUNT.png", bbox_inches='tight')
    plt.show()


def plot_ratio_of_risky_function(risk_ratios):
    plt.figure(figsize=(6, 5), dpi=600)
    ax = plt.subplot()

    bins = np.linspace(0, 1, 26)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    counts, _ = np.histogram(risk_ratios, bins=bins)
    total = sum(counts)
    cumulative_ratios = np.cumsum(counts) / total if total > 0 else np.zeros_like(counts)

    ax.bar(
        bin_centers,
        cumulative_ratios,
        width=0.04,
        color="gray",
        edgecolor='black',
        linewidth=1.2,
        zorder=10,
        align='center',
        antialiased=False
    )

    for i in range(12):
        ax.axhline(0.4 + i * 0.05, linestyle='--', color="lightgray", alpha=0.3)

    ax.grid(axis="y", alpha=0.4, linewidth=1.2)
    ax.set_ylim(0.2, 1.05)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Risk Ratio (Vulnerable/Used APIs)", fontsize=23)
    ax.set_ylabel("Ratio of Triples", fontsize=24)
    ax.tick_params(axis='both', labelsize=22)

    plt.tight_layout()
    plt.savefig("./RISKY_FUNCTION_RATIO.png", bbox_inches='tight')
    plt.show()
def plot_risk_data(all_list):
    """
    输入格式：
    [
        [5,1], #下游组件使用了5个函数，1个是可达的
        [6,0]
    ]
    """
    used_num=0
    reached_num=0
    zero_num=0

    reached_fun_num_list = []

    risk_ratios = []
    for used_fun_num, reached_fun_num in all_list:
        if used_fun_num == 0:
            continue
        used_num+=used_fun_num
        reached_num+=reached_fun_num
        ratio = reached_fun_num / used_fun_num
        if ratio == 0:
            zero_num+=1
            continue
        risk_ratios.append(ratio)

        if reached_fun_num == 0:
            continue
        reached_fun_num_list.append(reached_fun_num)
    average = np.mean(risk_ratios)
    print("使用的函数数目", used_num)
    print("有风险的函数数目", reached_num)
    print("无漏洞函数调用的三元组", zero_num)
    print("平均风险率",average)

    plot_ratio_of_risky_function(risk_ratios)
    plot_number_of_risky_function(reached_fun_num_list)


def main():
    """主函数，调用加载数据、处理数据、绘制图表"""
    analyze_data = load_analyze_data('data.pkl')  # 替换为你的实际路径
    path_len_dict = process_path_num_data(analyze_data)
    plot_risk_data(path_len_dict)



if __name__ == '__main__':
    main()
