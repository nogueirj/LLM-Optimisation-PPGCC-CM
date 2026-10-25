# StarCode Zero Shooting Prompt - starcoder1:42b

Task: Modify and optimize the input code to improve its performance (by re-factoring, re-ordering code, or improving the numerical algorithm) while keeping the original semantics (do not change numerical results). The goal is to minimize run time.

You are an expert in High-Performance Computing, C, OpenMP, and C++ compilers.

Goal:
Minimize the run-time of the input code while keeping the original semantics (i.e. do not change numerical results).

Input:
A PolyBench benchmark program in the PolyBench C 3.2 benchmark suite.

Note: For this assignment, do NOT modify existing PolyBench C 3.2 benchmark programs. Instead, modify the corresponding input file in our collection of PolyBench C 3.2 input files (you will find them in the files with a .txt extension).

Constraints:
- Assume compilation with: g++ -O3 -fopenmp -I [polybench_path]

Output format:
Optimized Kernel  (modified PolyBench source code):
