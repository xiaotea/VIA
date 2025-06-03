import json
import numpy as np
import matplotlib.pyplot as plt
import pickle

# 加载数据
with open('data.pkl', 'rb') as f:
    analyze_data = pickle.load(f)

print(len(analyze_data))

reached_count = 0
all_reached = 0
all_edge = 0
dep_edges = 0


for x in analyze_data:
    if analyze_data[x]["deploy_paths"] !=[]:
        reached_count+=1
    if analyze_data[x]["all_paths"] !=[]:
        all_reached+=1
    for y in analyze_data[x]["deploy_dependency"]:
        dep_edges+= len(analyze_data[x]["deploy_dependency"][y])
    for y in analyze_data[x]["all_dependency"]:
        all_edge+= len(analyze_data[x]["all_dependency"][y])

print("所有依赖边个数", all_edge)
print("仅部署依赖边个数", dep_edges)
print("仅部署可达", reached_count)
print("所有可达", all_reached)