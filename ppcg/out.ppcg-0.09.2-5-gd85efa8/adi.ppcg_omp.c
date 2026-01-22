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
      #pragma omp parallel for
      for (int c1 = 1; c1 < n - 1; c1 += 1) {
        v[0][c1] = 1.;
        p[c1][0] = 0.;
        q[c1][0] = v[0][c1];
        for (int c2 = 1; c2 < n - 1; c2 += 1) {
          p[c1][c2] = ((-c) / ((a * p[c1][c2 - 1]) + b));
          q[c1][c2] = ((((((-d) * u[c2][c1 - 1]) + ((1. + (2. * d)) * u[c2][c1])) - (f * u[c2][c1 + 1])) - (a * q[c1][c2 - 1])) / ((a * p[c1][c2 - 1]) + b));
        }
      }
      #pragma omp parallel for
      for (int c1 = 1; c1 < n - 1; c1 += 1) {
        v[n - 1][c1] = 1.;
        for (int c2 = 2; c2 < n; c2 += 1)
          v[n - c2][c1] = ((p[c1][n - c2] * v[n - c2 + 1][c1]) + q[c1][n - c2]);
      }
      #pragma omp parallel for
      for (int c1 = 1; c1 < n - 1; c1 += 1) {
        p[c1][0] = 0.;
        u[c1][0] = 1.;
        q[c1][0] = u[c1][0];
        for (int c2 = 1; c2 < n - 1; c2 += 1) {
          p[c1][c2] = ((-f) / ((d * p[c1][c2 - 1]) + e));
          q[c1][c2] = ((((((-a) * v[c1 - 1][c2]) + ((1. + (2. * a)) * v[c1][c2])) - (c * v[c1 + 1][c2])) - (d * q[c1][c2 - 1])) / ((d * p[c1][c2 - 1]) + e));
        }
      }
      #pragma omp parallel for
      for (int c1 = 1; c1 < n - 1; c1 += 1) {
        u[c1][n - 1] = 1.;
        for (int c2 = 2; c2 < n; c2 += 1)
          u[c1][n - c2] = ((p[c1][n - c2] * u[c1][n - c2 + 1]) + q[c1][n - c2]);
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
