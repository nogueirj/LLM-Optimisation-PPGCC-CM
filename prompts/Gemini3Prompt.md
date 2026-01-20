Task: Annotate a PolyBench C kernel with OpenMP pragmas.

You are an expert in High-Performance Computing, C, and OpenMP.

Objective:
Improve performance by adding OpenMP pragmas to the existing kernel,
WITHOUT modifying the original C code logic, structure, or statements.

STRICT CONSTRAINTS (must be followed exactly):
- DO NOT change, remove, reorder, or refactor any C code.
- DO NOT introduce new variables or temporary buffers.
- DO NOT change loop bounds, nesting, or conditions.
- ONLY add OpenMP pragmas (#pragma omp ...) immediately before existing loops.
- Do NOT add OpenMP directives inside loop bodies.
- Numerical results must remain identical.

Instructions:
1. Analyze the loop nest and identify data dependencies.
2. Select loops that are safe to parallelize.
3. Insert appropriate OpenMP pragmas using:
   - private / shared
   - collapse (only if fully safe)
   - schedule (prefer static)
4. Do NOT use reduction unless strictly required for correctness.
5. Assume compilation with: gcc -O3 -fopenmp.

Output format (follow exactly):
Analysis:
<short and technical analysis>

Optimized Kernel (OpenMP annotations only):
```c
```