/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* heat-3d.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "heat-3d.h"


/* Array initialization. */
static
void init_array (int n,
		 DATA_TYPE POLYBENCH_3D(A,N,N,N,n,n,n),
		 DATA_TYPE POLYBENCH_3D(B,N,N,N,n,n,n))
{
  int i, j, k;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      for (k = 0; k < n; k++)
        A[i][j][k] = B[i][j][k] = (DATA_TYPE) (i + j + (n-k))* 10 / (n);
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_3D(A,N,N,N,n,n,n))

{
  int i, j, k;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("A");
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      for (k = 0; k < n; k++) {
         if ((i * n * n + j * n + k) % 20 == 0) fprintf(POLYBENCH_DUMP_TARGET, "\n");
         fprintf(POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, A[i][j][k]);
      }
  POLYBENCH_DUMP_END("A");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_heat_3d(int tsteps,
		      int n,
		      DATA_TYPE POLYBENCH_3D(A,N,N,N,n,n,n),
		      DATA_TYPE POLYBENCH_3D(B,N,N,N,n,n,n))
{
  int t, i, j, k;

    /* ppcg generated CPU code */
    
    #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
    #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
    for (int c1 = 0; c1 <= n + 36; c1 += 32)
      for (int c2 = ppcg_max(0, ((n - c1 + 60) % 32) - n + c1 - 28); c2 <= ppcg_min(n + 36, n + c1 + 28); c2 += 32)
        for (int c3 = ppcg_max(ppcg_max(0, ((n - c1 + 60) % 32) - n + c1 - 28), ((n - c2 + 60) % 32) - n + c2 - 28); c3 <= ppcg_min(ppcg_min(n + 36, n + c1 + 28), n + c2 + 28); c3 += 32)
          for (int c4 = ppcg_max(ppcg_max(ppcg_max(0, -n + (n + c1 + 1) / 2 + 1), -n + (n + c2 + 1) / 2 + 1), -n + (n + c3 + 1) / 2 + 1); c4 <= ppcg_min(ppcg_min(ppcg_min(19, (c1 / 2) + 15), (c2 / 2) + 15), (c3 / 2) + 15); c4 += 1)
            for (int c5 = ppcg_max(ppcg_max(ppcg_max(0, -n - c1 + c2 + 3), -n - c1 + c3 + 3), -c1 + 2 * c4); c5 <= ppcg_min(31, n - c1 + 2 * c4 - 2); c5 += 1)
              for (int c6 = ppcg_max(ppcg_max(ppcg_max(0, -n - c2 + c3 + 3), -c2 + 2 * c4), -n + c1 - c2 + c5 + 3); c6 <= ppcg_min(ppcg_min(31, n - c2 + 2 * c4 - 2), n + c1 - c2 + c5 - 3); c6 += 1)
                for (int c7 = ppcg_max(ppcg_max(ppcg_max(0, -c3 + 2 * c4), -n + c1 - c3 + c5 + 3), -n + c2 - c3 + c6 + 3); c7 <= ppcg_min(ppcg_min(ppcg_min(31, n - c3 + 2 * c4 - 2), n + c1 - c3 + c5 - 3), n + c2 - c3 + c6 - 3); c7 += 1) {
                  if (n + 2 * c4 >= c1 + c5 + 3 && n + 2 * c4 >= c2 + c6 + 3 && n + 2 * c4 >= c3 + c7 + 3)
                    B[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 1] = ((((0.125 * ((A[c1 - 2 * c4 + c5 + 2][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 1] - (2. * A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 1])) + A[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 1])) + (0.125 * ((A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 2][c3 - 2 * c4 + c7 + 1] - (2. * A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 1])) + A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7 + 1]))) + (0.125 * ((A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 2] - (2. * A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 1])) + A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7]))) + A[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7 + 1]);
                  if (c1 + c5 >= 2 * c4 + 1 && c2 + c6 >= 2 * c4 + 1 && c3 + c7 >= 2 * c4 + 1)
                    A[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7] = ((((0.125 * ((B[c1 - 2 * c4 + c5 + 1][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7] - (2. * B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7])) + B[c1 - 2 * c4 + c5 - 1][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7])) + (0.125 * ((B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6 + 1][c3 - 2 * c4 + c7] - (2. * B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7])) + B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6 - 1][c3 - 2 * c4 + c7]))) + (0.125 * ((B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7 + 1] - (2. * B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7])) + B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7 - 1]))) + B[c1 - 2 * c4 + c5][c2 - 2 * c4 + c6][c3 - 2 * c4 + c7]);
                }

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;
  int tsteps = TSTEPS;

  /* Variable declaration/allocation. */
  POLYBENCH_3D_ARRAY_DECL(A, DATA_TYPE, N, N, N, n, n, n);
  POLYBENCH_3D_ARRAY_DECL(B, DATA_TYPE, N, N, N, n, n, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_heat_3d (tsteps, n, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(B));

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
