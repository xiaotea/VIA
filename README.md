# Short Paths, Real Risks: A Large-Scale Empirical Study of Dependency Relationships in PyPI Ecosystem

## Open-Source Dataset, Analysis Framework, and Tools Overview

To foster reproducibility and community-driven advancements, we release a comprehensive open-source package comprising datasets, analysis methods, and empirical results from our large-scale study of the PyPI ecosystem.

### Dataset
We construct a large-scale dataset for Python vulnerability impact analysis, containing **315,191 triples** of the form  
`&lt;CVE, vulnerable component, downstream component&gt;`.  

The dataset includes:
- **3,839** verified patches  
- **6,676** vulnerability locations  
- **851** unique vulnerabilities  
- **5,794** vulnerable component versions  
- **63,791** downstream component versions  

Each record is further annotated with:
- Declarative and deployed dependency graphs  
- Propagation paths  
- Call-graph validation results  

### Analysis Process
Our framework follows a **two-stage methodology**:

1. **Component Usage Verification** — parse source code imports to construct deployed dependency graphs, exposing both redundant and latent dependencies.  
2. **Code Invocation Verification** — integrate call-graph tracing (e.g., PyCG) to confirm whether vulnerable code blocks are actually invoked along dependency paths.  

This combined approach enables precise filtering of false positives while prioritizing vulnerabilities with real security impact.

### Tools
We provide modular static analysis tools for:
- Extracting real dependency graphs from source code  
- Comparing declarative vs. deployed dependencies to detect redundant and latent dependencies  
- Performing scalable call-path analysis with a divide-and-conquer algorithm to assess code-level reachability  

These tools are open-sourced and designed for integration into CI/CD pipelines and downstream vulnerability triage workflows.

### Empirical Results
Our findings demonstrate that:
- **41%** of declared dependencies are redundant, while **20%** of real dependencies are latent  
- Vulnerability reachability rapidly decays with path length: **99%** of reachable cases occur within three layers, whereas paths longer than six layers are effectively non-propagating  
- Only **5.5%** of reported vulnerabilities pose real risks after validating both dependency usage and code invocation  

---

Together, the open dataset, analysis framework, and released results provide a rigorous foundation for future research, reproducibility studies, and the development of more accurate vulnerability detection tools.


---

## Folder Structure

\`\`\`
.
├─ AnalyzeResult
│  └─ Realistic Dependency Extraction \& Vulnerable Code Call Path Analysis（Results archived in AnalyzeResult/Realistic Dependency Extraction \& Vulnerable Code Call Path Analysis/AnalyzeRes.7z.）
│
├─ DataSet
│   Triad.csv — \<vulnerability–vulnerable component–downstream component> triples
│   VUL_FUNs.csv — vulnerable functions metadata
│   VUL_patch.csv — patches
│
├─ RQ_data
│  ├─ dataset_code_stats
│  ├─ RQ1
│  │   └─ downloads_data
│  ├─ RQ2
│  └─ summary
│   Experimental data for research questions (RQ1–RQ2), including:
│   - Preprocessed statistics
│   - Data visualizations and figures from the paper
│
└─ Tool
   └─ PathFind
      ├─ core
      ├─ pycg_ex
      ├─ utils
      ├─ tool
      └─ data
\`\`\`

---

## Core Modules

- **Deployed Dependency Extraction Method**  
- **Call Path Analysis for Vulnerable Code**  

---

## Usage
Please refer to [\`Tool/README.md\`](Tool/README.md) for installation, dependencies, and execution instructions.
