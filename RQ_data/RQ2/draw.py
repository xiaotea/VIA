import json
import matplotlib.pyplot as plt
import pickle

data_dict = pickle.load(open("data.pkl", "rb"))

def get_mistake_res():
    """
    该函数用于根据不同的漏洞检测工具（如 PyPA、Google 等）是否受影响，分类收集它们的检测结果。
    解释如下：
        初始化四个空列表，用于存储各工具的误报结果。
        遍历 data_dict 中的每个 CVE 及其相关的漏洞信息。
        对每个组件检查其是否被某个工具标记为受影响，若受影响则将对应结果加入临时列表。
        若临时列表非空，则将其加入全局结果列表。
        最后返回四个工具各自的误报结果列表。
    """

    false_list_pypa = []
    false_list_google = []
    false_list_pip_audit = []
    false_list_safety = []


    for cve_name, vul_dict in data_dict.items():
        _false_list_pypa = []
        _false_list_google = []
        _false_list_pip_audit = []
        _false_list_safety = []
        for com_name ,affeted_dict in vul_dict.items():
            if "pysec_affect" in affeted_dict and affeted_dict["pysec_affect"]:
                _false_list_pypa.append(affeted_dict["ans_results"])
            if "google_affect" in affeted_dict and affeted_dict["google_affect"]:
                _false_list_google.append(affeted_dict["ans_results"])
            if "pip_audit_affect" in affeted_dict and affeted_dict["pip_audit_affect"]:
                _false_list_pip_audit.append(affeted_dict["ans_results"])
            if "safety_affect" in affeted_dict and affeted_dict["safety_affect"]:
                _false_list_safety.append(affeted_dict["ans_results"])
        if _false_list_pypa:
            false_list_pypa.append(_false_list_pypa)
        if _false_list_google:
            false_list_google.append(_false_list_google)
        if _false_list_pip_audit:
            false_list_pip_audit.append(_false_list_pip_audit)
        if _false_list_safety:
            false_list_safety.append(_false_list_safety)


        if sum(1 for x in _false_list_pypa if not x) == len(_false_list_pypa):
            print(cve_name)


    return false_list_pypa,false_list_google,false_list_pip_audit,false_list_safety

false_list_pypa,false_list_google,false_list_pip_audit,false_list_safety = get_mistake_res()



"""
false_list_pypa  demo 
[[True, True, True, True, True, True], [True, True, True, True], [False, False, False], [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False], [True, True], [True, True, True, True, True, True, True, True, True, True, True, True, False, False, False, False, False, False, False, False, True, True, True], [True, True], [True, True, True, True], [False, False, False], [True, True, True, True, True, True, True, False, False, False, False], [True, True, True, True], [True, True, True, True], [True, True, True, True, True], [True, True], [True, True, True, True, True, True, True, True, True, True, True, True], [True], [True, True], [False, False, False, False, False, False, False, False, False, False, False, False, True, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True], [True, True, True, True, True, True, True, True, True, True, True], [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True], [False, False, True, True, True, True, True, True], [True, True, False, True, True, True, True, True, True, True, True, True], [False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True], [False, False, False, False, True, True, True, True, True, True, False, True], [True, True], [True, True, True, True], [True, True, True, True, True, True, True, True, True, True], [True, True], [True, True, True, True, True], [True, True, True, True, True], [True, True], [True, True, True, True, True, True, True, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True], [True, True, True, True, True, True, False], [True, True, True, True, True, True, True, True, True, True, True], [True, True, True, True, True, True, True, True, True, True, True], [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True], [True], [False, False, False, False, False, False, False, False, False, False, False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, True, True, True, True, True], [True, True, True, True, True, True, True, True, True], [True, True, True, True, True, True, True, True], [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True], [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True], [True, True, True, True], [True, True, True, True, True, False, True, True, True, True, True, True, True, True, True], [False, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True], [True, True, True, True], [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, False, True, True, True, True, True, True, True, True, False, False, False, True, True, False, True, True, True, False], [True, True, True, True, True, True, True], [True, True, True, True, True, True]]

True :组件版本被开源漏洞库声明受影响，实际该组件版本也受影响  ，数据库或者检测正确
False :组件版本被开源漏洞库声明受影响，实际该组件版本不受影响 ， 数据库或者检测错误
列表中每一个子列表是一个漏洞对应不同版本的检测结果
绘制两个图象
1. 各个开源组/工具针对所有组件版本检测总数，误报的数量，误报的比例
2. 各个开源组/工具针对每个漏洞误报的比例，误报比例为在子数组中False的数量/数组长度
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import seaborn as sns
import pandas as pd

# plt.rcParams["font.family"] = "Times New Roman"
# sns.set(style="whitegrid")

# --------- 示例假数据（请替换为你自己的） ---------
# false_list_pypa, false_list_google, false_list_pip_audit, false_list_safety = [...]

# --------- 通用统计函数 ---------
def compute_overall_metrics(result_lists):
    total = sum(len(sublist) for sublist in result_lists)
    false_count = sum(result is False for sublist in result_lists for result in sublist)
    return total, false_count, false_count / total if total > 0 else 0

def compute_per_vuln_ratios(result_lists):
    return [sublist.count(False) / len(sublist) for sublist in result_lists if len(sublist) > 0]

# --------- 数据准备 ---------
tool_names = ['PyPA', 'Deps.dev', 'pip-audit', 'Safety']

tool_data = [false_list_pypa, false_list_google, false_list_pip_audit, false_list_safety]

totals, falses, rates = [], [], []
per_vuln_ratios_all = []

for data in tool_data:
    total, false_count, rate = compute_overall_metrics(data)
    totals.append(total)
    falses.append(false_count)
    rates.append(rate)
    per_vuln_ratios_all.append(compute_per_vuln_ratios(data))

# --------- 图1：整体误报统计 ---------
x = np.arange(len(tool_names))
width = 0.4

fig, ax1 = plt.subplots(figsize=(8, 5), dpi=600, constrained_layout=True)
ax2 = ax1.twinx()

bar1 = ax1.bar(x - width/2, totals, width, label='Affected Versions', color='#74a892', edgecolor='black')
bar2 = ax1.bar(x + width/2, falses, width, label='Incorrect Versions', color='#c7522a', edgecolor='black')
ax2.plot(x, [r * 100 for r in rates], 'o--', color='#008585', label='Incorrect Version Rate', linewidth=2)




ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}k'))
ax1.set_ylabel('Count', fontsize=24)
# ax2.set_ylabel('Incorrectly Affected Version Rate (%)', fontsize=16)
ax1.set_xticks(x)
ax1.set_xticklabels(tool_names, fontsize=26, rotation=15, ha='center')

# ax1.set_xticklabels(tool_names, fontsize=24)
ax1.tick_params(axis='both', labelsize=26)
ax2.tick_params(right=False, labelright=False,axis='y', labelsize=24)

ax2.set_ylim(0, 40)

# Offset text font (科学计数说明)
ax1.yaxis.get_offset_text().set_fontsize(18)
ax1.yaxis.get_offset_text().set_horizontalalignment("center")
ax2.yaxis.get_offset_text().set_fontsize(18)
ax2.yaxis.get_offset_text().set_horizontalalignment("center")

# 柱状图标签
# for rect in bar1 + bar2:
#     height = rect.get_height()
#     ax1.annotate(f'{height}', xy=(rect.get_x() + rect.get_width()/2, height),
#                  xytext=(0, 3), textcoords="offset points", ha='center', fontsize=20)

# 折线图标注
for i, rate in enumerate(rates):
    ax2.annotate(f'{rate * 100:.1f}%', xy=(x[i], rate * 100), xytext=(0, 8),
                 textcoords="offset points", ha='center', fontsize=20, color='black')

# 图例合并
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax1.legend(lines + lines2,
           labels + labels2, loc='upper right',
           fontsize=19,
           title_fontsize=24, frameon=False)

# ax1.legend(lines + lines2,
#            labels + labels2,
#
#            bbox_to_anchor=(1.1, 0.5),  # 以坐标定位 (x, y)
#            fontsize=20,
#            title_fontsize=24,
#            frameon=False)

plt.savefig("Fraction-of-Incorrectly-Affected-Versions.png", dpi=600, bbox_inches="tight")

# --------- 图2：每个漏洞误报率的 ECDF 曲线 ---------
data_for_ecdf = []
zero_fp_info = {}
one_fp_info = {}

for tool, ratios in zip(tool_names, per_vuln_ratios_all):
    for val in ratios:
        data_for_ecdf.append({"Tool": tool, "False Positive Ratio": val})
    total = len(ratios)
    zero_fp_info[tool] = sum(1 for val in ratios if val == 0) / total if total else 0
    one_fp_info[tool] = sum(1 for val in ratios if val == 1) / total if total else 0

df_ecdf = pd.DataFrame(data_for_ecdf)
fig, ax = plt.subplots(figsize=(8, 5), dpi=600, constrained_layout=True)

sns.ecdfplot(
    data=df_ecdf,
    x="False Positive Ratio",
    hue="Tool",
    palette=["#008585", "#74a892", "#c7522a", "#e5c185"],
    linewidth=2,
    ax=ax
)

ax.set_xlim(0.0, 1.05)
ax.set_ylim(0.5, 1.05)

# 注释：误报率为 0 的比例
for i, tool in enumerate(tool_names):
    ratio = zero_fp_info[tool]
    ax.annotate(
        f'{ratio * 100:.1f}%',
        xy=(0.0, ratio),
        xytext=(45, 5 + i * 18),
        textcoords='offset points',
        fontsize=20,
        color='black',
        ha='left',
        va='center',
        arrowprops=dict(arrowstyle='->', lw=1, color='black')
    )

# 坐标和标签
ax.set_xlabel("Incorrect Version Ratio per CVE", fontsize=24)
ax.set_ylabel("Cumulative Distribution", fontsize=24)
ax.tick_params(axis='both', labelsize=24)


ticks = [0.0, 0.4, 0.8,1.0]
ax.set_xticks(ticks)        # 设置刻度位置
# xticks = ax.get_xticks()
# ax.set_xticks(xticks[::2])  # 每隔一个取一个刻度显示


# 图例设置
ax.legend_.set_title("Database-and-Tools")
ax.legend_.get_title().set_fontsize(24)
for text in ax.legend_.get_texts():
    text.set_fontsize(24)

ax.grid(True, linestyle='--', alpha=0.5)
plt.savefig("Fraction-of-Incorrectly-Affected-Versions-per-CVE.png", dpi=600, bbox_inches="tight")
plt.show()
