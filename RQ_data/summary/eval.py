import json
import os

import pickle

affected_data_path = r"..\RQ2\data.pkl"
ctx_data = pickle.load(open(affected_data_path, "rb"))

version_effect = set()
# 争议
diff_version_effect = set()
for cve_name, cve_data in ctx_data.items():
    for com_name, com_data in cve_data.items():
        keys = ["pysec_affect", "google_affect", "safety_affect", "pip_audit_affect"]
        existing_values = [com_data[key] for key in keys if key in com_data]
        if existing_values and len(set(existing_values)) == 2:  # 有争议的
            diff_version_effect.add(cve_name + "@" + com_name)

        if com_data.get("ans_results"):
            version_effect.add(cve_name + "@" + com_name)

dep_reached_up_downstream = set()
with open(r"..\RQ3\data.pkl", "rb") as f:
    ctx_data = pickle.load(f)
for dep_com, dep_data in ctx_data.items():
    if dep_data.get("deploy_paths", []) != []:
        dep_reached_up_downstream.add(dep_com)

vul_code_reached_up_downstream = set()
with open(r"..\RQ4\data.pkl", "rb") as f:
    ctx_data = pickle.load(f)
for trip_name, trip_data in ctx_data.items():
    if trip_data.get("is_reachable"):
        print(trip_name)
        vul_code_reached_up_downstream.add(trip_name)

all_versions_effect_num = 0
all_versions_not_effect_num = 0

all_dep_effect_num = 0
all_dep_not_effect_num = 0

all_invoked_effected_num = 0
all_invoked_not_effected_num = 0

a1,a2,b1,b2,c1,c2 = 0,0,0,0,0,0

_diff_num_list  = [0,0,0]

for trip_name in os.listdir(r"F:\python_project\AnalyzeRes"):


    cve_version = "@".join(trip_name.split("@")[:3])
    dep_name = "@".join(trip_name.split("@")[1:])

    # if cve_version in diff_version_effect:
    #     continue


    if cve_version in diff_version_effect:
        _diff_num_list[0] += 1
        if cve_version in version_effect:
            _diff_num_list[1] += 1
        else:
            _diff_num_list[2] += 1

    if cve_version in version_effect:
        all_versions_effect_num += 1
        a1 +=1
        if trip_name in vul_code_reached_up_downstream:
            c1 +=1
        if dep_name in dep_reached_up_downstream:
            b1 +=1

    else:
        if dep_name in dep_reached_up_downstream:
            b2 +=1
        if trip_name in vul_code_reached_up_downstream:
            c2 +=1
        all_versions_not_effect_num += 1
        a2+=1

    if dep_name in dep_reached_up_downstream:
        all_dep_effect_num += 1
    else:
        all_dep_not_effect_num += 1

    if trip_name in vul_code_reached_up_downstream:
        all_invoked_effected_num += 1
    else:
        all_invoked_not_effected_num += 1

print(a1,a2,b1,b2,c1,c2)
print(_diff_num_list)