Task: Annotate an existing PolyBench C kernel with OpenMP pragmas.

You are an expert in High-Performance Computing, C, and OpenMP.

Goal:
Insert OpenMP pragmas to parallelize the kernel for performance, WITHOUT modifying the original C code logic, loop structure, or statements.

Strict Rules (must follow exactly):
- DO NOT change, reorder, remove, or refactor any line of C code.
- DO NOT introduce temporary variables.
- DO NOT change loop bounds or nesting.
- ONLY add OpenMP pragmas (#pragma omp ...) immediately before existing loops.
- Numerical results must remain identical.

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
- Section: "Analysis"
- Section: "Optimized Kernel (OpenMP annotations only)"
- Section: "Rationale"

Kernel to annotate:
```c
```