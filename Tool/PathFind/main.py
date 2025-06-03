import os
import json
import shutil
from pathlib import Path

from core.machinery.software import SoftwareManager
from core.machinery.dependency import DependencyManager
from core.utils.utils import find_software_list, output_errors
from core.utils.common import get_local_software_version

# 路径配置
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
LOG_DIR = BASE_DIR / 'logs'
RESULT_DIR = BASE_DIR / 'AnalyzeRes'


def list_existing_results():
    return os.listdir(RESULT_DIR)


def is_dir_exceeding_size(path, max_bytes=10 * 1024 * 1024):
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, filenames in os.walk(path) for f in filenames)
    return total > max_bytes


def write_failure_log(entry, retries=3):
    try:
        with open(LOG_DIR / "fail_log", 'a') as f:
            f.write(entry + '\n')
    except IOError as e:
        if output_errors:
            print(e)
        if retries > 0:
            write_failure_log(entry, retries - 1)


def analyze_vulnerability(upstream_name, upstream_version, downstream_name, downstream_version, cve_id,
                          dependencies=None, vuln_locations=None, mode=2, downstream_path=None):
    if vuln_locations is None:
        vuln_locations = []

    print("Starting analysis:", upstream_name, upstream_version, downstream_name, downstream_version, vuln_locations)

    # 获取软件列表
    software_list = [(d.split("@")[0], d.split("@")[1]) for d in dependencies] if dependencies \
        else find_software_list([(upstream_name, upstream_version)])

    # 本地版本替换及去重
    processed = []
    for name, version in software_list:
        if name in {downstream_name, upstream_name}:
            continue
        local_version = get_local_software_version(name, version)
        processed.append((name, local_version or version))
    software_list = processed

    # 加入下游组件路径（如指定）
    if downstream_path:
        downstream_name = os.path.basename(downstream_path)
        shutil.copytree(downstream_path, DATA_DIR / f"{downstream_name}@")
        software_list.append((downstream_name, ""))

    # 确保上下游组件也在分析中
    software_list += [(downstream_name, downstream_version), (upstream_name, upstream_version)]
    if not software_list:
        print("No dependencies found.")
        return {}

    software_objects, version_map = [], {}
    for name, version in software_list:
        if name in version_map:
            continue
        software = SoftwareManager(name, version)
        if software.software_name.lower() in {upstream_name.lower(),
                                              downstream_name.lower()} and not software.have_source_code:
            if output_errors:
                print(f"No source for {software.software_name}")
            return None
        if not software.have_source_code:
            continue
        software_objects.append(software)
        version_map[name] = version

    # 分析部署依赖
    for sw in software_objects:
        sw.analyze_used_package_list()

    dep_mgr = DependencyManager(software_objects, upstream_name, downstream_name, vuln_locations)
    dep_mgr.find_dependency_path()
    dep_mgr.analyze_fun_path()

    result = {
        "vulnerability_loc": vuln_locations,
        "Versionmap": version_map,
        "deploy_dependency": dep_mgr.get_deploy_dependency_map(),
        "all_dependency": dep_mgr.get_all_dependency_map(),
    }

    if mode == 2:
        result.update({
            "dependency_path": dep_mgr.find_dependency_path(),
            "fun_reachable_info": dep_mgr.get_fun_reachable_info(),
        })

    return result


def run_analysis(up_name, up_version, down_name, down_version, cve, dep_list, vuln_locs, mode=2, down_path=None):
    filename = f"{cve}@{up_name}@{up_version}@{down_name}@{down_version}"
    print(f"Processing: {filename}")

    result = analyze_vulnerability(
        up_name, up_version,
        down_name, down_version,
        cve, dep_list,
        vuln_locs, mode, down_path
    )

    if not result:
        print("Analysis failed:", filename)
        return

    with open(RESULT_DIR / filename, 'w') as f:
        print("Saving results for", filename)
        json.dump(result, f, indent=4)

    return result


# 示例用法
if __name__ == "__main__":
    upstream = "urllib3"
    upstream_ver = "2.0.3"
    downstream = "docker"
    downstream_ver = "6.1.3"
    cve_id = "CVE-2024-37891"
    dependencies_list = [
        "requests@2.31.0",
        "docker@6.1.3",
        "urllib3@2.0.3"
    ]
    locations = [
        "src/urllib3/util/retry.Retry"
    ]

    result = run_analysis(upstream, upstream_ver, downstream, downstream_ver, cve_id, dependencies_list, locations)
    print("Analysis Result:\n", result)
