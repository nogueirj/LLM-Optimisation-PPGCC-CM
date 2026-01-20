# StarCode Zero Shooting Prompt - starcoder2:15b

Task: Add OpenMP pragmas to an existing PolyBench C kernel.

You are an expert in High-Performance Computing, C, and OpenMP.

Goal:
Parallelize the kernel using OpenMP pragmas WITHOUT modifying the original C code in any way.

STRICT CONSTRAINTS (must be followed exactly):
- DO NOT change any C statement.
- DO NOT add, remove, or reorder loops.
- DO NOT introduce new variables.
- DO NOT change loop bounds or conditions.
- DO NOT refactor expressions.
- ONLY add lines starting with: #pragma omp
- Pragmas must be placed immediately before existing loops.
- Numerical results must remain identical.

Instructions:
1. Analyze the loop nest and identify data dependencies.
2. Select loops that are safe to parallelize.
3. Insert appropriate OpenMP pragmas using:
   - private / shared
   - collapse (only if fully safe)
   - schedule (prefer static)
4. Do NOT use reduction unless strictly required.
5. Assume compilation with: gcc -O3 -fopenmp.

Output format (follow exactly):
Analysis:
<short analysis>

Optimized Kernel (OpenMP annotations only):
```c
```
