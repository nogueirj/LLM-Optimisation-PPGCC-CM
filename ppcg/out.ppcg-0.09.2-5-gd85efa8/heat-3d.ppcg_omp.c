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
    for (int c0 = 1; c0 <= 20; c0 += 1)
      for (int c1 = 2 * c0 + 1; c1 < n + 2 * c0; c1 += 1)
        for (int c2 = ppcg_max(2 * c0 + 1, -n + c1 + 3); c2 < ppcg_min(n + 2 * c0, n + c1 - 2); c2 += 1)
          #pragma omp parallel for
          for (int c3 = ppcg_max(ppcg_max(2 * c0 + 1, -n + c1 + 3), -n + c2 + 3); c3 < ppcg_min(ppcg_min(n + 2 * c0, n + c1 - 2), n + c2 - 2); c3 += 1) {
            if (c1 >= 2 * c0 + 2 && c2 >= 2 * c0 + 2 && c3 >= 2 * c0 + 2)
              A[-2 * c0 + c1 - 1][-2 * c0 + c2 - 1][-2 * c0 + c3 - 1] = ((((0.125 * ((B[-2 * c0 + c1][-2 * c0 + c2 - 1][-2 * c0 + c3 - 1] - (2. * B[-2 * c0 + c1 - 1][-2 * c0 + c2 - 1][-2 * c0 + c3 - 1])) + B[-2 * c0 + c1 - 2][-2 * c0 + c2 - 1][-2 * c0 + c3 - 1])) + (0.125 * ((B[-2 * c0 + c1 - 1][-2 * c0 + c2][-2 * c0 + c3 - 1] - (2. * B[-2 * c0 + c1 - 1][-2 * c0 + c2 - 1][-2 * c0 + c3 - 1])) + B[-2 * c0 + c1 - 1][-2 * c0 + c2 - 2][-2 * c0 + c3 - 1]))) + (0.125 * ((B[-2 * c0 + c1 - 1][-2 * c0 + c2 - 1][-2 * c0 + c3] - (2. * B[-2 * c0 + c1 - 1][-2 * c0 + c2 - 1][-2 * c0 + c3 - 1])) + B[-2 * c0 + c1 - 1][-2 * c0 + c2 - 1][-2 * c0 + c3 - 2]))) + B[-2 * c0 + c1 - 1][-2 * c0 + c2 - 1][-2 * c0 + c3 - 1]);
            if (n + 2 * c0 >= c1 + 2 && n + 2 * c0 >= c2 + 2 && n + 2 * c0 >= c3 + 2)
              B[-2 * c0 + c1][-2 * c0 + c2][-2 * c0 + c3] = ((((0.125 * ((A[-2 * c0 + c1 + 1][-2 * c0 + c2][-2 * c0 + c3] - (2. * A[-2 * c0 + c1][-2 * c0 + c2][-2 * c0 + c3])) + A[-2 * c0 + c1 - 1][-2 * c0 + c2][-2 * c0 + c3])) + (0.125 * ((A[-2 * c0 + c1][-2 * c0 + c2 + 1][-2 * c0 + c3] - (2. * A[-2 * c0 + c1][-2 * c0 + c2][-2 * c0 + c3])) + A[-2 * c0 + c1][-2 * c0 + c2 - 1][-2 * c0 + c3]))) + (0.125 * ((A[-2 * c0 + c1][-2 * c0 + c2][-2 * c0 + c3 + 1] - (2. * A[-2 * c0 + c1][-2 * c0 + c2][-2 * c0 + c3])) + A[-2 * c0 + c1][-2 * c0 + c2][-2 * c0 + c3 - 1]))) + A[-2 * c0 + c1][-2 * c0 + c2][-2 * c0 + c3]);
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
