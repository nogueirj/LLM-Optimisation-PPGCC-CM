/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* seidel-2d.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "seidel-2d.h"


/* Array initialization. */
static
void init_array (int n,
		 DATA_TYPE POLYBENCH_2D(A,N,N,n,n))
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      A[i][j] = ((DATA_TYPE) i*(j+2) + 2) / n;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_2D(A,N,N,n,n))

{
  int i, j;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("A");
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
      if ((i * n + j) % 20 == 0) fprintf(POLYBENCH_DUMP_TARGET, "\n");
      fprintf(POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, A[i][j]);
    }
  POLYBENCH_DUMP_END("A");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_seidel_2d(int tsteps,
		      int n,
		      DATA_TYPE POLYBENCH_2D(A,N,N,n,n))
{
  int t, i, j;

  /* ppcg generated CPU code */
  
  #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
  #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
  for (int c0 = 0; c0 < tsteps; c0 += 32)
    for (int c1 = c0; c1 <= ppcg_min(n + tsteps - 4, n + c0 + 28); c1 += 32)
      for (int c2 = c0 + c1; c2 <= ppcg_min(ppcg_min(ppcg_min(2 * n + 2 * tsteps - 8, 2 * n + 2 * c0 + 56), n + tsteps + c1 + 27), n + c0 + c1 + 59); c2 += 32)
        for (int c3 = ppcg_max(ppcg_max(ppcg_max(0, -n - c0 + c1 + 3), -n - c0 - c1 + c2 - 28), (c2 / 2) - n - c0 + 3); c3 <= ppcg_min(ppcg_min(31, tsteps - c0 - 1), (c2 / 2) - c0 + 15); c3 += 1)
          for (int c4 = ppcg_max(ppcg_max(0, c0 - c1 + c3), -n - c0 - c1 + c2 - c3 + 3); c4 <= ppcg_min(ppcg_min(31, n + c0 - c1 + c3 - 3), -c0 - c1 + c2 - c3 + 31); c4 += 1)
            for (int c5 = ppcg_max(0, c0 + c1 - c2 + c3 + c4); c5 <= ppcg_min(31, n + c0 + c1 - c2 + c3 + c4 - 3); c5 += 1)
              A[-c0 + c1 - c3 + c4 + 1][-c0 - c1 + c2 - c3 - c4 + c5 + 1] = (((((((((A[-c0 + c1 - c3 + c4][-c0 - c1 + c2 - c3 - c4 + c5] + A[-c0 + c1 - c3 + c4][-c0 - c1 + c2 - c3 - c4 + c5 + 1]) + A[-c0 + c1 - c3 + c4][-c0 - c1 + c2 - c3 - c4 + c5 + 2]) + A[-c0 + c1 - c3 + c4 + 1][-c0 - c1 + c2 - c3 - c4 + c5]) + A[-c0 + c1 - c3 + c4 + 1][-c0 - c1 + c2 - c3 - c4 + c5 + 1]) + A[-c0 + c1 - c3 + c4 + 1][-c0 - c1 + c2 - c3 - c4 + c5 + 2]) + A[-c0 + c1 - c3 + c4 + 2][-c0 - c1 + c2 - c3 - c4 + c5]) + A[-c0 + c1 - c3 + c4 + 2][-c0 - c1 + c2 - c3 - c4 + c5 + 1]) + A[-c0 + c1 - c3 + c4 + 2][-c0 - c1 + c2 - c3 - c4 + c5 + 2]) / 9.);

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;
  int tsteps = TSTEPS;

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, N, N, n, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(A));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_seidel_2d (tsteps, n, POLYBENCH_ARRAY(A));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(A)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);

  return 0;
}
