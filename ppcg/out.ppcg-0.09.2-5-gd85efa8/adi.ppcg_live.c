/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* adi.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "adi.h"


/* Array initialization. */
static
void init_array (int n,
		 DATA_TYPE POLYBENCH_2D(u,N,N,n,n))
{
  int i, j;

  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++)
      {
	u[i][j] =  (DATA_TYPE)(i + n-j) / n;
      }
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_2D(u,N,N,n,n))

{
  int i, j;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("u");
  for (i = 0; i < n; i++)
    for (j = 0; j < n; j++) {
      if ((i * n + j) % 20 == 0) fprintf(POLYBENCH_DUMP_TARGET, "\n");
      fprintf (POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, u[i][j]);
    }
  POLYBENCH_DUMP_END("u");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
/* Based on a Fortran code fragment from Figure 5 of
 * "Automatic Data and Computation Decomposition on Distributed Memory Parallel Computers"
 * by Peizong Lee and Zvi Meir Kedem, TOPLAS, 2002
 */
static
void kernel_adi(int tsteps, int n,
		DATA_TYPE POLYBENCH_2D(u,N,N,n,n),
		DATA_TYPE POLYBENCH_2D(v,N,N,n,n),
		DATA_TYPE POLYBENCH_2D(p,N,N,n,n),
		DATA_TYPE POLYBENCH_2D(q,N,N,n,n))
{
  int t, i, j;
  DATA_TYPE DX, DY, DT;
  DATA_TYPE B1, B2;
  DATA_TYPE mul1, mul2;
  DATA_TYPE a, b, c, d, e, f;

  /* ppcg generated CPU code */
  
  #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
  #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
  if (n >= 3 && tsteps >= 1) {
    B1 = 2.;
    DT = (1. / ((double) (tsteps)));
    DX = (1. / ((double) (n)));
    mul1 = ((B1 * DT) / (DX * DX));
    a = ((-mul1) / 2.);
    DY = (1. / ((double) (n)));
    B2 = 1.;
    mul2 = ((B2 * DT) / (DY * DY));
    d = ((-mul2) / 2.);
    e = (1. + mul2);
    b = (1. + mul1);
    c = a;
    f = d;
    for (int c0 = 1; c0 <= tsteps; c0 += 1) {
      for (int c1 = 0; c1 < n - 2; c1 += 32)
        for (int c2 = 0; c2 < n - 1; c2 += 32)
          for (int c3 = 0; c3 <= ppcg_min(31, n - c1 - 3); c3 += 1) {
            if (c2 == 0) {
              v[0][c1 + c3 + 1] = 1.;
              q[c1 + c3 + 1][0] = v[0][c1 + c3 + 1];
              p[c1 + c3 + 1][0] = 0.;
            }
            for (int c4 = ppcg_max(0, -c2 + 1); c4 <= ppcg_min(31, n - c2 - 2); c4 += 1) {
              p[c1 + c3 + 1][c2 + c4] = ((-c) / ((a * p[c1 + c3 + 1][c2 + c4 - 1]) + b));
              q[c1 + c3 + 1][c2 + c4] = ((((((-d) * u[c2 + c4][c1 + c3]) + ((1. + (2. * d)) * u[c2 + c4][c1 + c3 + 1])) - (f * u[c2 + c4][c1 + c3 + 2])) - (a * q[c1 + c3 + 1][c2 + c4 - 1])) / ((a * p[c1 + c3 + 1][c2 + c4 - 1]) + b));
            }
          }
      for (int c1 = 0; c1 < n - 2; c1 += 32)
        for (int c2 = 0; c2 < n - 1; c2 += 32)
          for (int c3 = 0; c3 <= ppcg_min(31, n - c1 - 3); c3 += 1) {
            if (c2 == 0)
              v[n - 1][c1 + c3 + 1] = 1.;
            for (int c4 = ppcg_max(0, -c2 + 1); c4 <= ppcg_min(31, n - c2 - 2); c4 += 1)
              v[n - c2 - c4 - 1][c1 + c3 + 1] = ((p[c1 + c3 + 1][n - c2 - c4 - 1] * v[n - c2 - c4][c1 + c3 + 1]) + q[c1 + c3 + 1][n - c2 - c4 - 1]);
          }
      for (int c1 = 0; c1 < n - 2; c1 += 32)
        for (int c2 = 0; c2 < n - 1; c2 += 32)
          for (int c3 = 0; c3 <= ppcg_min(31, n - c1 - 3); c3 += 1) {
            if (c2 == 0) {
              p[c1 + c3 + 1][0] = 0.;
              u[c1 + c3 + 1][0] = 1.;
              q[c1 + c3 + 1][0] = u[c1 + c3 + 1][0];
            }
            for (int c4 = ppcg_max(0, -c2 + 1); c4 <= ppcg_min(31, n - c2 - 2); c4 += 1) {
              p[c1 + c3 + 1][c2 + c4] = ((-f) / ((d * p[c1 + c3 + 1][c2 + c4 - 1]) + e));
              q[c1 + c3 + 1][c2 + c4] = ((((((-a) * v[c1 + c3][c2 + c4]) + ((1. + (2. * a)) * v[c1 + c3 + 1][c2 + c4])) - (c * v[c1 + c3 + 2][c2 + c4])) - (d * q[c1 + c3 + 1][c2 + c4 - 1])) / ((d * p[c1 + c3 + 1][c2 + c4 - 1]) + e));
            }
          }
      for (int c1 = 0; c1 < n - 2; c1 += 32)
        for (int c2 = 0; c2 < n - 1; c2 += 32)
          for (int c3 = 0; c3 <= ppcg_min(31, n - c1 - 3); c3 += 1) {
            if (c2 == 0)
              u[c1 + c3 + 1][n - 1] = 1.;
            for (int c4 = ppcg_max(0, -c2 + 1); c4 <= ppcg_min(31, n - c2 - 2); c4 += 1)
              u[c1 + c3 + 1][n - c2 - c4 - 1] = ((p[c1 + c3 + 1][n - c2 - c4 - 1] * u[c1 + c3 + 1][n - c2 - c4]) + q[c1 + c3 + 1][n - c2 - c4 - 1]);
          }
    }
  }
}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;
  int tsteps = TSTEPS;

  /* Variable declaration/allocation. */
  POLYBENCH_2D_ARRAY_DECL(u, DATA_TYPE, N, N, n, n);
  POLYBENCH_2D_ARRAY_DECL(v, DATA_TYPE, N, N, n, n);
  POLYBENCH_2D_ARRAY_DECL(p, DATA_TYPE, N, N, n, n);
  POLYBENCH_2D_ARRAY_DECL(q, DATA_TYPE, N, N, n, n);


  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(u));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_adi (tsteps, n, POLYBENCH_ARRAY(u), POLYBENCH_ARRAY(v), POLYBENCH_ARRAY(p), POLYBENCH_ARRAY(q));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(u)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(u);
  POLYBENCH_FREE_ARRAY(v);
  POLYBENCH_FREE_ARRAY(p);
  POLYBENCH_FREE_ARRAY(q);

  return 0;
}
