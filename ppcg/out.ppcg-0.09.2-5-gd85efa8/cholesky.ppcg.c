/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* cholesky.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "cholesky.h"


/* Array initialization. */
static
void init_array(int n,
		DATA_TYPE POLYBENCH_2D(A,N,N,n,n))
{
  int i, j;

  for (i = 0; i < n; i++)
    {
      for (j = 0; j <= i; j++)
	A[i][j] = (DATA_TYPE)(-j % n) / n + 1;
      for (j = i+1; j < n; j++) {
	A[i][j] = 0;
      }
      A[i][i] = 1;
    }

  /* Make the matrix positive semi-definite. */
  int r,s,t;
  POLYBENCH_2D_ARRAY_DECL(B, DATA_TYPE, N, N, n, n);
  for (r = 0; r < n; ++r)
    for (s = 0; s < n; ++s)
      (POLYBENCH_ARRAY(B))[r][s] = 0;
  for (t = 0; t < n; ++t)
    for (r = 0; r < n; ++r)
      for (s = 0; s < n; ++s)
	(POLYBENCH_ARRAY(B))[r][s] += A[r][t] * A[s][t];
    for (r = 0; r < n; ++r)
      for (s = 0; s < n; ++s)
	A[r][s] = (POLYBENCH_ARRAY(B))[r][s];
  POLYBENCH_FREE_ARRAY(B);

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
    for (j = 0; j <= i; j++) {
    if ((i * n + j) % 20 == 0) fprintf (POLYBENCH_DUMP_TARGET, "\n");
    fprintf (POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, A[i][j]);
  }
  POLYBENCH_DUMP_END("A");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_cholesky(int n,
		     DATA_TYPE POLYBENCH_2D(A,N,N,n,n))
{
  int i, j, k;


  /* ppcg generated CPU code */
  
  #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
  #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
  for (int c0 = 0; c0 < n; c0 += 32)
    for (int c1 = c0; c1 < n; c1 += 32)
      for (int c2 = c0; c2 <= c1 + 30; c2 += 32) {
        if (n >= c2 + 2) {
          for (int c3 = 0; c3 <= ppcg_min(ppcg_min(ppcg_min(31, n - c0 - 3), -c0 + c1 + 29), -c0 + c2 + 30); c3 += 1) {
            if (c1 == c0 && c2 == c0) {
              A[c0 + c3][c0 + c3] = sqrt(A[c0 + c3][c0 + c3]);
            } else if (c2 == c1 && c1 >= c0 + c3 + 2) {
              A[c1][c1] -= (A[c1][c0 + c3] * A[c1][c0 + c3]);
            }
            if (c2 == c1 && c0 + c3 + 1 >= c1) {
              if (c1 == c0)
                A[c0 + c3 + 1][c0 + c3] /= A[c0 + c3][c0 + c3];
              A[c0 + c3 + 1][c0 + c3 + 1] -= (A[c0 + c3 + 1][c0 + c3] * A[c0 + c3 + 1][c0 + c3]);
            }
            for (int c4 = ppcg_max(ppcg_max(0, -c1 + c2 + 1), c0 - c1 + c3 + 2); c4 <= ppcg_min(31, n - c1 - 1); c4 += 1) {
              if (c2 == c0)
                A[c1 + c4][c0 + c3] /= A[c0 + c3][c0 + c3];
              for (int c5 = ppcg_max(0, c0 - c2 + c3 + 1); c5 <= ppcg_min(31, c1 - c2 + c4 - 1); c5 += 1)
                A[c1 + c4][c2 + c5] -= (A[c1 + c4][c0 + c3] * A[c2 + c5][c0 + c3]);
              if (c2 == c1)
                A[c1 + c4][c1 + c4] -= (A[c1 + c4][c0 + c3] * A[c1 + c4][c0 + c3]);
            }
          }
          if (n >= c0 + 34 && c1 >= c0 + 32 && c2 == c0) {
            for (int c4 = 0; c4 <= ppcg_min(31, n - c1 - 1); c4 += 1)
              if (c1 + c4 >= c0 + 32)
                A[c1 + c4][c0 + 31] /= A[c0 + 31][c0 + 31];
          } else if (c0 + 33 == n && c1 + 1 == n && c2 + 33 == n) {
            A[n - 1][n - 2] /= A[n - 2][n - 2];
          } else if (n >= c0 + 33 && c1 == c0 && c2 == c0) {
            A[c0 + 30][c0 + 30] = sqrt(A[c0 + 30][c0 + 30]);
            A[c0 + 31][c0 + 30] /= A[c0 + 30][c0 + 30];
            A[c0 + 31][c0 + 31] -= (A[c0 + 31][c0 + 30] * A[c0 + 31][c0 + 30]);
            if (n >= c0 + 34) {
              A[c0 + 31][c0 + 31] = sqrt(A[c0 + 31][c0 + 31]);
            } else {
              A[n - 2][n - 2] = sqrt(A[n - 2][n - 2]);
            }
          }
        } else {
          for (int c3 = 0; c3 <= ppcg_min(31, n - c0 - 3); c3 += 1)
            A[n - 1][n - 1] -= (A[n - 1][c0 + c3] * A[n - 1][c0 + c3]);
        }
        if (n >= c0 + 2 && c0 + 33 >= n && c1 + 32 >= n && c2 == c1) {
          if (c1 == c0) {
            A[n - 2][n - 2] = sqrt(A[n - 2][n - 2]);
            A[n - 1][n - 2] /= A[n - 2][n - 2];
          }
          A[n - 1][n - 1] -= (A[n - 1][n - 2] * A[n - 1][n - 2]);
        }
        if (c0 + 32 >= n && c1 == c0 && c2 == c0)
          A[n - 1][n - 1] = sqrt(A[n - 1][n - 1]);
      }

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, N, N, n, n);

  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(A));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_cholesky (n, POLYBENCH_ARRAY(A));

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
