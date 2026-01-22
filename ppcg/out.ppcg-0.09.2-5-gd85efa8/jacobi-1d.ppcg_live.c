/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* jacobi-1d.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "jacobi-1d.h"


/* Array initialization. */
static
void init_array (int n,
		 DATA_TYPE POLYBENCH_1D(A,N,n),
		 DATA_TYPE POLYBENCH_1D(B,N,n))
{
  int i;

  for (i = 0; i < n; i++)
      {
	A[i] = ((DATA_TYPE) i+ 2) / n;
	B[i] = ((DATA_TYPE) i+ 3) / n;
      }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_1D(A,N,n))

{
  int i;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("A");
  for (i = 0; i < n; i++)
    {
      if (i % 20 == 0) fprintf(POLYBENCH_DUMP_TARGET, "\n");
      fprintf(POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, A[i]);
    }
  POLYBENCH_DUMP_END("A");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_jacobi_1d(int tsteps,
			    int n,
			    DATA_TYPE POLYBENCH_1D(A,N,n),
			    DATA_TYPE POLYBENCH_1D(B,N,n))
{
  int t, i;

  /* ppcg generated CPU code */
  
  #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
  #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
  if (n >= 3)
    for (int c0 = 0; c0 < tsteps; c0 += 32)
      for (int c1 = 2 * c0; c1 <= ppcg_min(2 * tsteps + n - 4, n + 2 * c0 + 60); c1 += 32)
        for (int c2 = ppcg_max(0, -n - c0 + (n + c1 + 1) / 2 + 1); c2 <= ppcg_min(ppcg_min(31, tsteps - c0 - 1), (c1 / 2) - c0 + 15); c2 += 1)
          for (int c3 = ppcg_max(0, 2 * c0 - c1 + 2 * c2); c3 <= ppcg_min(31, n + 2 * c0 - c1 + 2 * c2 - 2); c3 += 1) {
            if (n + 2 * c0 + 2 * c2 >= c1 + c3 + 3)
              B[-2 * c0 + c1 - 2 * c2 + c3 + 1] = (0.33333 * ((A[-2 * c0 + c1 - 2 * c2 + c3] + A[-2 * c0 + c1 - 2 * c2 + c3 + 1]) + A[-2 * c0 + c1 - 2 * c2 + c3 + 2]));
            if (c1 + c3 >= 2 * c0 + 2 * c2 + 1)
              A[-2 * c0 + c1 - 2 * c2 + c3] = (0.33333 * ((B[-2 * c0 + c1 - 2 * c2 + c3 - 1] + B[-2 * c0 + c1 - 2 * c2 + c3]) + B[-2 * c0 + c1 - 2 * c2 + c3 + 1]));
          }

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;
  int tsteps = TSTEPS;

  /* Variable declaration/allocation. */
  POLYBENCH_1D_ARRAY_DECL(A, DATA_TYPE, N, n);
  POLYBENCH_1D_ARRAY_DECL(B, DATA_TYPE, N, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_jacobi_1d(tsteps, n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(A)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(A);
  POLYBENCH_FREE_ARRAY(B);

  return 0;
}
