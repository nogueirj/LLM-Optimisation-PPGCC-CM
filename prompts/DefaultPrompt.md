# High-Performance Computing OpenMP Optimization Prompt

Task: Annotate the provided PolyBench C program with OpenMP pragmas.

You are an expert in High-Performance Computing (HPC), C programming, and OpenMP optimization.

Goal:
Insert OpenMP pragmas to parallelize the kernel for maximum performance, WITHOUT modifying the original C code logic, loop structure, or statements.

Strict Rules (must follow exactly):
- DO NOT change, reorder, remove, or refactor any line of existing C code.
- DO NOT introduce temporary variables or buffers.
- DO NOT change loop bounds or nesting.
- ONLY add OpenMP pragmas (#pragma omp ...) immediately before safe loops.
- Numerical results must remain completely identical.
- You MUST return the COMPLETE, FULL compilable C source code file (including headers, array initializations, kernel function, and main) in a single ```c ... ``` code block.

Instructions:
1. Briefly analyze the loop nest and data dependencies.
2. Decide which loops are safe to parallelize.
3. Add OpenMP pragmas with correct clauses:
   - private / shared
   - collapse (only if safe)
   - schedule (choose static unless clearly suboptimal)
4. Do NOT use reduction unless strictly necessary.
5. Assume compilation with: gcc -O3 -fopenmp.

Output format:
Analysis:
<Brief analysis of data dependencies and parallelization strategy>

Optimized Kernel:
```c
<The entire, complete C source code with OpenMP pragmas inserted>
```
