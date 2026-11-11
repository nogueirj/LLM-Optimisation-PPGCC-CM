Task: Annotate an existing C kernel with OpenMP pragmas.

You are an expert in High-Performance Computing, C, and OpenMP.

Goal:
Insert OpenMP pragmas to parallelize the kernel for performance, WITHOUT modifying the original C code logic, loop structure, or statements.

Strict Rules (must follow exactly):
- DO NOT change, reorder, remove, or refactor any line of C code (keep every comment, #include header, helper function, and main() intact).
- DO NOT introduce temporary variables.
- DO NOT change loop bounds or nesting.
- ONLY add OpenMP pragmas (#pragma omp ...) immediately before existing safe `for` loops inside the main `kernel_*` function (between `#pragma scop` and `#pragma endscop`). DO NOT add pragmas inside `init_array`, `print_array`, or `main`.
- NEVER place two `#pragma omp` directives consecutively; every `#pragma omp` line MUST be immediately followed on the very next line by a `for (...)` statement.
- Always use `#pragma omp parallel for` (do NOT omit the `for` keyword when annotating a `for` loop without braces).
- CRITICAL C89 RULE: Because loop variables (`i`, `j`, `k`) are declared at the top of the function (`int i, j, k;`), whenever you parallelize an outer loop over `i`, you MUST explicitly list all inner loop counters in `private(...)` (e.g., `#pragma omp parallel for private(j)` for a 2D nest or `#pragma omp parallel for private(j, k)` for a 3D nest). Leaving `j` or `k` out of `private(...)` makes them shared across threads and causes race conditions!
- NEVER list a loop iteration variable (`i`, `j`, `k`) or pointer/array parameter inside `firstprivate(...)`; use `private(...)` for inner loop indices.
- Check array write indices carefully to prevent race conditions: if an outer loop over `i` updates an array indexed by `j` (e.g., `y[j] += ...`), either use a valid C OpenMP 4.5 array-section reduction (e.g., `reduction(+:y[:ny])`) or only parallelize the loops whose left-hand-side write index includes the parallelized loop variable.
- You MUST return the COMPLETE, FULL, COMPILABLE C source file from the opening comment/#include to the closing `}` of `main()` inside a single ```c ... ``` block.
- Numerical results must remain identical.

Instructions:
1. Briefly analyze the loop nest and data dependencies in the `kernel_*` function.
2. Decide which loops are safe to parallelize.
3. Add OpenMP pragmas with correct clauses:
   - private / shared
   - collapse (only if safe and loops are perfectly nested)
   - schedule (choose static unless clearly suboptimal)
4. Do NOT use reduction unless strictly necessary.
5. Assume compilation with: gcc -O3 -fopenmp.

Output format:
- Section: "Analysis"
- Section: "Optimized Kernel (OpenMP annotations only)"
- Section: "Rationale"

Kernel to annotate:

```c
{code}
```
