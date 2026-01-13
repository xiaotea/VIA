# Python Vulnerability Triad Dataset (Vuln–Component–Downstream)

## 1. Overview

This release contains a large-scale dataset of Python-related vulnerabilities and their downstream exposure in the PyPI ecosystem. Each record in the core file (Triad.csv) is a <vulnerability, vulnerable component version, downstream component version> triple, augmented with one or more dependency chains (i.e., paths) from the downstream component version to the vulnerable component version, extracted from the declarative component dependency graph (CDG-Declarative). These triples can be used to study dependency accuracy, reachability, and downstream risk at scale.

### Key scale (this release)

- **315,191** triads (rows) in `Triad.csv`
- **756** unique vulnerabilities (CVE IDs) in `Triad.csv`
- **4,640** unique vulnerable component versions (e.g., `jinja2@3.1.2`)
  - **251** unique vulnerable package names (without versions)
- **49,407** unique downstream component versions
  - **24,840** unique downstream package names (without versions)

Additional mappings provide patch references, vulnerable function anchors, and CWE labels.

## 2. Files and Formats

All files are in CSV format.

| File | Size | Purpose |
|---|---:|---|
| `Triad.csv` | ~301 MB | Core triads and dependency paths |
| `VUL_patch.csv` | ~366 KB | CVE → patch/repair references (URLs) |
| `VUL_FUNs.csv` | ~346 KB | CVE → vulnerable function anchors (semi-colon separated) |
| `cve_cwe_mapping.csv` | ~20 KB | CVE → CWE list (from NVD labels) |
| `cwe_stats.csv` | ~1.8 KB | Aggregated CWE frequency statistics |

## 3. Schema

### 3.1 `Triad.csv` (no header)

**Columns (in order):**

1. `vuln_id` — Vulnerability identifier (CVE), e.g., `CVE-2024-49766`
2. `component` — Vulnerable component **name@version**, e.g., `werkzeug@3.0.0`
3. `downstream` — Downstream component **name@version**, e.g., `langchain-g4f@0.1.0`
4. `dep_paths` — A JSON-encoded list of dependency chains from `downstream` to `component`.

**`dep_paths` format**

- `dep_paths` is a JSON list: `List[List[str]]`
- Each inner list is one dependency chain, represented as an ordered sequence of `pkg@ver`
  from **downstream → ... → vulnerable component**, inclusive.

Example (pretty-printed for readability):

```json
[
  ["langchain-g4f@0.1.0", "flask@3.0.0", "werkzeug@3.0.0"],
  ["langchain-g4f@0.1.0", "flask-cors@4.0.0", "flask@3.0.0", "werkzeug@3.0.0"]
]
```

Interpretation:
- The downstream package depends on the vulnerable package either directly (path length 2)
  or transitively (path length ≥ 3), and multiple distinct dependency chains may exist.

### 3.2 `VUL_patch.csv` (no header)

**Columns (in order):**

1. `vuln_id` — CVE ID
2. `patch_links` — One or more patch references (URLs).  
   Multiple links are separated by newline characters within the same cell.

Typical link types include:
- GitHub commit URLs, PR commit lists, release notes, security advisories, or official patch pages.

### 3.3 `VUL_FUNs.csv` (no header)

**Columns (in order):**

1. `vuln_id` — CVE ID
2. `vul_functions` — Vulnerable function anchors, separated by semicolons (`;`).

Each anchor is a path-like string that helps locate the vulnerable logic in the codebase
(e.g., `module/path.Class.method` or `path/to/file.function`).

### 3.4 `cve_cwe_mapping.csv`

**Columns:**
- `CVE` — CVE ID
- `CWE_List` — One or more CWE labels, separated by `;` (or occasionally `,`).

Notes:
- Some entries use NVD special labels such as `NVD-CWE-Other` or `NVD-CWE-noinfo`.

### 3.5 `cwe_stats.csv`

**Columns:**
- `CWE` — CWE label (including NVD special labels)
- `Count` — Frequency across the `CWE_List` occurrences (i.e., CVEs may contribute more than one count)

## 4. Dataset Statistics (computed from the included files)

### 4.1 Dependency-path characteristics (`Triad.csv`)

- **Paths per triad**: mean **5.71**, median **1**, p90 **5**, p99 **38**, max **4,888**
- **Dependency-chain length** (number of `pkg@ver` nodes per chain):
  - minimum length: **2** (direct dependency)
  - maximum length: **17**
  - shortest-chain length per triad: mean **2.50**, median **2**
- **Direct vs transitive exposure**:
  - triads with at least one **direct** dependency path (shortest length = 2): **~61.0%**
  - triads with only **transitive** paths (shortest length > 2): **~39.0%**

### 4.2 Patch references (`VUL_patch.csv`)

- **2,605** CVEs with patch references
- **3,837** URL references in this release (newline-separated links)

> Note: the paper reports 3,839 valid patches; minor discrepancies can occur due to dead links,
> non-URL sources (e.g., blog reproduction records), or release-time curation.

### 4.3 Vulnerable-function anchors (`VUL_FUNs.csv`)

- **1,713** CVEs with function-level anchors
- functions per CVE: mean **3.90**, median **2**, max **48**
- All **756** CVEs in `Triad.csv` are covered by `VUL_FUNs.csv`.

### 4.4 CWE labels (`cve_cwe_mapping.csv`, `cwe_stats.csv`)

- **756** CVEs have CWE labels in `cve_cwe_mapping.csv`
- **919** total CWE occurrences after splitting multi-label entries
- Most frequent labels (top 5 by count):
  - `CWE-79` (XSS): 68
  - `NVD-CWE-noinfo`: 67
  - `CWE-22` (Path Traversal): 54
  - `CWE-200` (Information Exposure): 44
  - `CWE-20` (Improper Input Validation): 37

## 5. Data Collection and Construction (as described in the paper)

This dataset follows the paper’s collection pipeline and filtering criteria.

### 5.1 Vulnerability collection

We collected Python-related vulnerabilities from multiple public sources:
- PyPA DB, Deps.dev DB, GitHub, and official project websites.

To resolve identifier inconsistencies (CVE/GHSA/PYSEC), we performed manual cleaning and deduplication
using alias fields and semantic comparison of descriptions, resulting in **3,179** vulnerabilities.
We then expanded coverage with a customized crawler (GitHub Issues/PRs/commits and official advisory/patch pages),
reaching **3,464** vulnerabilities.

### 5.2 Patch collection

Candidate patches were collected from:
- reference links in NVD, Deps.dev, and PyPA DB,
- plus supplemental mining from blogs/forums via search engines.

For cases without public patches, we used reproduction records and repository metadata to locate relevant code differences.
All candidate patches were manually inspected to remove non-security changes and to verify alignment with vulnerability
descriptions/types. In total, we collected **3,839** valid patches covering **2,605** vulnerabilities
(represented in `VUL_patch.csv` and partially reflected by `VUL_FUNs.csv`).

### 5.3 Downstream component collection

We collected downstream components (dependents) to approximate real-world exposed user groups.
Affected versions were identified using the `affected` field in vulnerability databases and NVD CPE.
Downstream dependents and declarative dependency graphs were gathered via:
- Deps.dev (“Dependents”), and
- Libraries.io (“Used by”).

Because some packages are very old or lack retrievable code/graphs, we discarded records without source code
for either downstream or vulnerable components, or without dependency graphs.

Finally, we built **315,191** \<vulnerability, component, downstream component\> triads (see `Triad.csv`).
