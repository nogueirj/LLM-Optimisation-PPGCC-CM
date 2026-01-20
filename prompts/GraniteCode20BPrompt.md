#Granite Code 20B Prompt
You are an expert in High-Performance Computing (HPC), C programming, and OpenMP optimization.

Your Task:
Annotate the provided PolyBench C kernel with OpenMP pragmas to parallelize loops and improve performance.

Strict Constraints (You MUST follow these):
1. NO Refactoring: Do not change, remove, reorder, or refactor any existing C code logic.
2. NO New Variables: Do not introduce new variables, temporary buffers, or macros.
3. NO Loop Changes: Do not change loop bounds, nesting, or step values.
4. Pragmas Only: ONLY add `#pragma omp ...` directives immediately before safe loops.
5. Location: Do NOT place OpenMP directives inside loop bodies (except atomic, if absolutely necessary, but prefer reduction on the loop).
6. Correctness: The numerical output must remain identical to the sequential version.

Optimization Guidelines:
1. Analyze Dependencies: Identify which loops carry dependencies and which are parallelizable.
2. Scoping: Correctly identify `shared` vs `private` variables. Loop iterators of parallel regions are private by default. Inner loop iterators defined outside the parallel region MUST be explicitly marked `private`.
3. Strategy:
   - Use `#pragma omp parallel for` for the outermost parallelizable loop.
   - Use `collapse(N)` if multiple outer loops are perfectly nested and independent.
   - Use `schedule(static)` for PolyBench kernels as the workload is uniform.
   - Use `reduction(operator:var)` only if there is a scalar dependency (accumulation).

Input Code:
```c
static
void kernel_atax(int nx, int ny,
		 DATA_TYPE POLYBENCH_2D(A,NX,NY,nx,ny),
		 DATA_TYPE POLYBENCH_1D(x,NY,ny),
		 DATA_TYPE POLYBENCH_1D(y,NY,ny),
		 DATA_TYPE POLYBENCH_1D(tmp,NX,nx))
{
  int i, j;

#pragma scop
  for (i = 0; i < _PB_NY; i++)
    y[i] = 0;
  for (i = 0; i < _PB_NX; i++)
    {
      tmp[i] = 0;
      for (j = 0; j < _PB_NY; j++)
	tmp[i] = tmp[i] + A[i][j] * x[j];
      for (j = 0; j < _PB_NY; j++)
	y[j] = y[j] + A[i][j] * tmp[i];
    }
#pragma endscop

}
```

Output Format:
Provide the output in the following format:

Analysis:
<Brief technical explanation of dependencies and strategy>

Optimized Code:
```c
<The full C code with OpenMP pragmas inserted>
