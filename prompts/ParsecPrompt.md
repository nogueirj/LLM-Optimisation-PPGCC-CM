Task: Annotate an existing PARSEC C kernel with OpenMP pragmas.

You are an expert in High-Performance Computing, C, and OpenMP.

Goal:
Insert OpenMP pragmas to parallelize the computational kernel for performance, WITHOUT modifying the original C code logic, loop structure, or statements.

Strict Rules (must follow exactly):
- DO NOT change, reorder, remove, or refactor any line of C code (keep every comment, #include header, helper function, and main() intact).
- DO NOT introduce temporary variables.
- DO NOT change loop bounds or nesting.
- ONLY add OpenMP pragmas (#pragma omp ...) immediately before existing safe `for` loops inside the main `kernel_*` function (between `#pragma scop` and `#pragma endscop`). DO NOT add pragmas inside `init_array`, `print_array`, helper functions, or `main`.
- NEVER place two `#pragma omp` directives consecutively; every `#pragma omp` line MUST be immediately followed on the very next line by a `for (...)` statement.
- Always use `#pragma omp parallel for` (do NOT omit the `for` keyword when annotating a `for` loop).
- CRITICAL C89 RULE: Because loop variables (`i`, `j`, `k`, `t`, `d`, `f`, `v`) and working scalar variables (`price`, `dist`, `diff`, `x_cost`, `dt`, `sqrt_dt`, `sum_price`, `sum_sq`, `rate_path`, `discount`, `shock`, `drift`, `vol`, `z`, `payoff`, `disc_payoff`, `dx`, `dy`, `dz`, `distSq`, `hmr`, `fpress`, `inv_rho`, `mask`, `has_item`, `count`, `score`, `w`) are declared at the top of `kernel_*`, whenever you parallelize a loop over an index (such as `i`, `t`, or `item`), you MUST explicitly list all inner loop counters and temporary scalar variables modified inside that loop in `private(...)`. Leaving inner loop counters or temporary scalars out of `private(...)` makes them shared across threads and causes race conditions!
- Do NOT parallelize sequential time-stepping or iterative outer loops (`for (fr = 0; ...)` or `for (step = 0; ...)` where iteration `fr+1` depends on arrays updated in iteration `fr`); instead, parallelize the spatial/data-parallel inner loops (`for (i = 0; ...)`).
- You MUST return the COMPLETE, FULL, COMPILABLE C source file from the opening comment/#include to the closing `}` of `main()` inside a single ```c ... ``` block.
- Numerical results must remain identical.

Instructions:
1. Briefly analyze the loop nest and data dependencies in the `kernel_*` function.
2. Decide which loops are safe to parallelize.
3. Add OpenMP pragmas with correct `private(...)` and `schedule(...)` clauses.
4. Assume compilation with: gcc -O3 -fopenmp.

Output format:
- Section: "Analysis"
- Section: "Optimized Kernel (OpenMP annotations only)"
- Section: "Rationale"

Kernel to annotate:

```c
{code}
```

