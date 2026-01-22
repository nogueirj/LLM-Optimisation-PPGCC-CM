/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* jacobi-2d.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "jacobi-2d.h"


/* Array initialization. */
static
void init_array (int n,
		 DATA_TYPE POLYBENCH_2D(A,N,N,n,n),
		 DATA_TYPE POLYBENCH_2D(B,N,N,n,n))
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      {
	A[i][j] = ((DATA_TYPE) i*(j+2) + 2) / n;
	B[i][j] = ((DATA_TYPE) i*(j+3) + 3) / n;
      }
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
void kernel_jacobi_2d(int tsteps,
			    int n,
			    DATA_TYPE POLYBENCH_2D(A,N,N,n,n),
			    DATA_TYPE POLYBENCH_2D(B,N,N,n,n))
{
  int t, i, j;

  /* ppcg generated CPU code */
  
  #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
  #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
  #define ppcg_fdiv_q(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
  for (int c0 = 0; c0 < tsteps; c0 += 32)
    for (int c1 = 2 * c0; c1 <= ppcg_min(n + 2 * tsteps - 4, n + 2 * c0 + 60); c1 += 32)
      for (int c2 = ppcg_max(2 * c0, 32 * ppcg_fdiv_q(-n + c1 + 3, 32)); c2 <= ppcg_min(ppcg_min(n + 2 * tsteps - 4, n + 2 * c0 + 60), n + c1 + 28); c2 += 32)
        for (int c3 = ppcg_max(ppcg_max(0, -n - c0 + (n + c1 + 1) / 2 + 1), -n - c0 + (n + c2 + 1) / 2 + 1); c3 <= ppcg_min(ppcg_min(ppcg_min(31, tsteps - c0 - 1), (c1 / 2) - c0 + 15), (c2 / 2) - c0 + 15); c3 += 1)
          for (int c4 = ppcg_max(ppcg_max(0, -n - c1 + c2 + 3), 2 * c0 - c1 + 2 * c3); c4 <= ppcg_min(31, n + 2 * c0 - c1 + 2 * c3 - 2); c4 += 1)
            for (int c5 = ppcg_max(ppcg_max(0, 2 * c0 - c2 + 2 * c3), -n + c1 - c2 + c4 + 3); c5 <= ppcg_min(ppcg_min(31, n + 2 * c0 - c2 + 2 * c3 - 2), n + c1 - c2 + c4 - 3); c5 += 1) {
              if (c1 + c4 >= 2 * c0 + 2 * c3 + 1 && c2 + c5 >= 2 * c0 + 2 * c3 + 1)
                A[-2 * c0 + c1 - 2 * c3 + c4][-2 * c0 + c2 - 2 * c3 + c5] = (0.20000000000000001 * ((((B[-2 * c0 + c1 - 2 * c3 + c4][-2 * c0 + c2 - 2 * c3 + c5] + B[-2 * c0 + c1 - 2 * c3 + c4][-2 * c0 + c2 - 2 * c3 + c5 - 1]) + B[-2 * c0 + c1 - 2 * c3 + c4][-2 * c0 + c2 - 2 * c3 + c5 + 1]) + B[-2 * c0 + c1 - 2 * c3 + c4 + 1][-2 * c0 + c2 - 2 * c3 + c5]) + B[-2 * c0 + c1 - 2 * c3 + c4 - 1][-2 * c0 + c2 - 2 * c3 + c5]));
              if (n + 2 * c0 + 2 * c3 >= c1 + c4 + 3 && n + 2 * c0 + 2 * c3 >= c2 + c5 + 3)
                B[-2 * c0 + c1 - 2 * c3 + c4 + 1][-2 * c0 + c2 - 2 * c3 + c5 + 1] = (0.20000000000000001 * ((((A[-2 * c0 + c1 - 2 * c3 + c4 + 1][-2 * c0 + c2 - 2 * c3 + c5 + 1] + A[-2 * c0 + c1 - 2 * c3 + c4 + 1][-2 * c0 + c2 - 2 * c3 + c5]) + A[-2 * c0 + c1 - 2 * c3 + c4 + 1][-2 * c0 + c2 - 2 * c3 + c5 + 2]) + A[-2 * c0 + c1 - 2 * c3 + c4 + 2][-2 * c0 + c2 - 2 * c3 + c5 + 1]) + A[-2 * c0 + c1 - 2 * c3 + c4][-2 * c0 + c2 - 2 * c3 + c5 + 1]));
            }

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;
  int tsteps = TSTEPS;

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, N, N, n, n);
  POLYBENCH_2D_ARRAY_DECL(B, DATA_TYPE, N, N, n, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_jacobi_2d(tsteps, n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

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
