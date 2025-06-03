===========================================
VIA: Real-World Automated Vulnerability Impact Analysis for the PyPI Ecosystem
===========================================

Overview
--------
VIA (Vulnerability Impact Analysis) is a framework designed to reduce false positive vulnerability alerts in the Python ecosystem. It combines Large Language Models (LLMs) and static analysis techniques to evaluate whether reported vulnerabilities truly affect downstream components.

The framework addresses three core issues:
1. Incorrect version-to-vulnerability mappings
2. Unused or undeclared dependencies
3. Vulnerable code that is never invoked

Our dataset consists of 577,329 vulnerability-component-component triples. Evaluation results show that only 3.7% of reported vulnerabilities pose actual threats.

Folder Structure
----------------
1. AnalyzeResult
   - Contains the output of VIA's core modules:
     * Vulnerability Existence Verification (LLM-based)
     * Realistic Dependency Extraction
     * Call Path Reachability Analysis

2. DataSet
   - Raw data used by VIA, including:
     * Vulnerability reports
     * PyPI component metadata
     * Ground truth version mappings
     * Evaluation-ready triple data

3. RQ_data
   - Experimental data for the research questions (RQ1–RQ5):
     * Preprocessed statistics
     * Data visualizations and figures from the paper

4. Tool
   - Full source code of the VIA framework, including:
     * LLM-based vulnerability checker
     * Deployed Dependency Extraction Method
     * Call Path Analysis for Vulnerable Code Method

Usage
-----
Refer to the `Tool/README.md` file for installation, dependencies, and execution instructions.

