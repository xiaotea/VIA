# Tool Usage Guide

This document explains the purpose and usage of the tools in the `Tool/` directory.  

## Directory Structure

- `PathFind/`: The main analysis tool, including:
  - **Dependency Extraction**: Identifies *actually used* dependencies from deployed source code.  
  - **Call Path Analysis**: Builds function-level call graphs and verifies whether vulnerable code is truly invoked.  
  - `AnalyzeRes/`: Stores intermediate and final analysis results.  
  - `core/`, `pycg_ex/`, `utils/`: Internal modules for parsing, call graph construction, and path search.  
  - `data/`: Example input data for testing.  

---

## 1. PathFind

PathFind integrates **realistic dependency extraction** and **vulnerable code call path analysis**, which together form the backbone of the framework.

### Key Features

- **Deployed Dependency Extraction**  
  Parses import statements in deployed source code to construct real dependency graphs, eliminating redundant dependencies and supplementing undeclared but used ones.  

- **Call Graph Generation**  
  Uses PyCG-based static analysis to build fine-grained function-level call graphs for each component.  

- **Call Path Analysis**  
  Performs stepwise search to determine whether vulnerable code is actually invoked along dependency paths, filtering out non-propagating vulnerabilities.  

### How to Use

1. **Install Dependencies**  
   The `PathFind` directory provides a `requirements.txt`. Install required packages before running analysis:  
   ```bash
   cd Tool/PathFind/
   pip install -r requirements.txt
