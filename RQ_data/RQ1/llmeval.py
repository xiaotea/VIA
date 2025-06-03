import pickle

with open("llm_eval.pkl", "rb") as f:
    all_res_dict = pickle.load(f)

from collections import defaultdict

# 存储最终评估结果：{model_name: {ablation_item: {"TP": .., "TN": .., "FP": .., "FN": ..}}}
eval_result = defaultdict(lambda: defaultdict(lambda: {"TP": 0, "TN": 0, "FP": 0, "FN": 0, "Total": 0}))

for cve_name, com_dict in all_res_dict.items():
    for com_name, model_dict in com_dict.items():
        std = model_dict.get("std", None)
        if std is None:
            continue
        for model_name, res_dict in model_dict.items():
            if model_name == "std":
                continue
            for ablation_item, pred in res_dict.items():
                if pred == std:
                    if pred:
                        eval_result[model_name][ablation_item]["TP"] += 1
                    else:
                        eval_result[model_name][ablation_item]["TN"] += 1
                else:
                    if pred:
                        eval_result[model_name][ablation_item]["FP"] += 1
                    else:
                        eval_result[model_name][ablation_item]["FN"] += 1
                eval_result[model_name][ablation_item]["Total"] += 1




# 打印结果
print("评估结果：\n")
for model_name, ablation_items in eval_result.items():
    if model_name=="Hunyuan-TurboS":
        continue
    print(f"Model: {model_name}")
    for ablation_item, metrics in ablation_items.items():
        TP = metrics["TP"]
        TN = metrics["TN"]
        FP = metrics["FP"]
        FN = metrics["FN"]
        total = metrics["Total"]

        accuracy = (TP + TN) / total if total > 0 else 0
        precision = TP / (TP + FP) if (TP + FP) > 0 else 0
        neg_precision = TN / (TN + FN) if (TN + FN) > 0 else 0

        print(f"  {ablation_item:<20} | TP: {TP:<3} TN: {TN:<3} FP: {FP:<3} FN: {FN:<3} "
              f"Acc: {accuracy:.3f}  Prec+: {precision:.3f}  Prec-: {neg_precision:.3f}")
    print()

import numpy as np

# 模型顺序：DeepSeek-R1, Gemini-2.5, Grok-3, OpenAI o3
full = [0.964, 0.924, 0.959, 0.910]
without_cg = [0.873, 0.914, 0.939, 0.872]
without_hits = [0.929, 0.904, 0.939, 0.883]

# 计算相对于 full 的提升（或下降）情况
cg_deltas = [f - c for f, c in zip(full, without_cg)]
hits_deltas = [f - h for f, h in zip(full, without_hits)]

# 打印每项差值
print("Delta due to CG removal:", cg_deltas)
print("Delta due to Hits removal:", hits_deltas)

# 平均变化值
avg_cg_delta = np.mean(cg_deltas)
avg_hits_delta = np.mean(hits_deltas)

print(f"\nAverage drop due to CG removal:   {avg_cg_delta:.3f}")
print(f"Average drop due to Hits removal: {avg_hits_delta:.3f}")