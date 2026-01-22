/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* trisolv.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "trisolv.h"


/* Array initialization. */
static
void init_array(int n,
		DATA_TYPE POLYBENCH_2D(L,N,N,n,n),
		DATA_TYPE POLYBENCH_1D(x,N,n),
		DATA_TYPE POLYBENCH_1D(b,N,n))
{
  int i, j;

  for (i = 0; i < n; i++)
    {
      x[i] = - 999;
      b[i] =  i ;
      for (j = 0; j <= i; j++)
	L[i][j] = (DATA_TYPE) (i+n-j+1)*2/n;
    }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_1D(x,N,n))

{
  int i;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("x");
  for (i = 0; i < n; i++) {
    fprintf (POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, x[i]);
    if (i % 20 == 0) fprintf (POLYBENCH_DUMP_TARGET, "\n");
  }
  POLYBENCH_DUMP_END("x");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_trisolv(int n,
		    DATA_TYPE POLYBENCH_2D(L,N,N,n,n),
		    DATA_TYPE POLYBENCH_1D(x,N,n),
		    DATA_TYPE POLYBENCH_1D(b,N,n))
{
  int i, j;

  /* ppcg generated CPU code */
  
  #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
  #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
  for (int c0 = 0; c0 < n; c0 += 32)
    for (int c1 = 0; c1 < n; c1 += 32) {
      if (n >= c0 + 2) {
        for (int c2 = 0; c2 <= ppcg_min(ppcg_min(31, n - c0 - 2), -c0 + c1 + 30); c2 += 1) {
          if (c0 >= 32 && c1 == c0 && c2 == 0) {
            x[c0] = (x[c0] / L[c0][c0]);
          } else if (c1 == c0 && c2 >= 1) {
            x[c0 + c2] = (x[c0 + c2] / L[c0 + c2][c0 + c2]);
          } else if (c0 == 0 && c1 == 0 && c2 == 0) {
            x[0] = b[0];
            x[0] = (x[0] / L[0][0]);
          }
          for (int c3 = ppcg_max(0, c0 - c1 + c2 + 1); c3 <= ppcg_min(31, n - c1 - 1); c3 += 1) {
            if (c0 == 0 && c2 == 0)
              x[c1 + c3] = b[c1 + c3];
            x[c1 + c3] -= (L[c1 + c3][c0 + c2] * x[c0 + c2]);
          }
        }
        if (c0 + 31 >= n && c1 == c0) {
          x[n - 1] = (x[n - 1] / L[n - 1][n - 1]);
        } else if (n >= c0 + 32 && c1 == c0) {
          x[c0 + 31] = (x[c0 + 31] / L[c0 + 31][c0 + 31]);
        }
      } else if (n >= 33 && c1 + 1 == n) {
        x[n - 1] = (x[n - 1] / L[n - 1][n - 1]);
      } else if (n == 1 && c1 == 0) {
        x[0] = b[0];
        x[0] = (x[0] / L[0][0]);
      }
    }

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(L, DATA_TYPE, N, N, n, n);
  POLYBENCH_1D_ARRAY_DECL(x, DATA_TYPE, N, n);
  POLYBENCH_1D_ARRAY_DECL(b, DATA_TYPE, N, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(L), POLYBENCH_ARRAY(x), POLYBENCH_ARRAY(b));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_trisolv (n, POLYBENCH_ARRAY(L), POLYBENCH_ARRAY(x), POLYBENCH_ARRAY(b));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(x)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(L);
  POLYBENCH_FREE_ARRAY(x);
  POLYBENCH_FREE_ARRAY(b);

  return 0;
}
