/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* correlation.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "correlation.h"


/* Array initialization. */
static
void init_array (int m,
		 int n,
		 DATA_TYPE *float_n,
		 DATA_TYPE POLYBENCH_2D(data,N,M,n,m))
{
  int i, j;

  *float_n = (DATA_TYPE)N;

  for (i = 0; i < N; i++)
    for (j = 0; j < M; j++)
      data[i][j] = (DATA_TYPE)(i*j)/M + i;

}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int m,
		 DATA_TYPE POLYBENCH_2D(corr,M,M,m,m))

{
  int i, j;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("corr");
  for (i = 0; i < m; i++)
    for (j = 0; j < m; j++) {
      if ((i * m + j) % 20 == 0) fprintf (POLYBENCH_DUMP_TARGET, "\n");
      fprintf (POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, corr[i][j]);
    }
  POLYBENCH_DUMP_END("corr");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_correlation(int m, int n,
			DATA_TYPE float_n,
			DATA_TYPE POLYBENCH_2D(data,N,M,n,m),
			DATA_TYPE POLYBENCH_2D(corr,M,M,m,m),
			DATA_TYPE POLYBENCH_1D(mean,M,m),
			DATA_TYPE POLYBENCH_1D(stddev,M,m))
{
  int i, j, k;

  DATA_TYPE eps = SCALAR_VAL(0.1);


  /* ppcg generated CPU code */
  
  {
    #pragma omp parallel for
    for (int c0 = 0; c0 < m - 1; c0 += 1)
      corr[c0][c0] = 1.;
    #pragma omp parallel for
    for (int c0 = 0; c0 < m; c0 += 1) {
      mean[c0] = 0.;
      for (int c1 = 0; c1 < n; c1 += 1)
        mean[c0] += data[c1][c0];
    }
    #pragma omp parallel for
    for (int c0 = 0; c0 < m; c0 += 1) {
      stddev[c0] = 0.;
      mean[c0] /= float_n;
      for (int c1 = 0; c1 < n; c1 += 1)
        stddev[c0] += ((data[c1][c0] - mean[c0]) * (data[c1][c0] - mean[c0]));
    }
    #pragma omp parallel for
    for (int c0 = 0; c0 < m; c0 += 1) {
      stddev[c0] /= float_n;
      stddev[c0] = sqrt(stddev[c0]);
      stddev[c0] = ((stddev[c0] <= eps) ? 1. : stddev[c0]);
    }
    #pragma omp parallel for
    for (int c0 = 0; c0 < n; c0 += 1)
      for (int c1 = 0; c1 < m; c1 += 1) {
        data[c0][c1] -= mean[c1];
        data[c0][c1] /= (sqrt(float_n) * stddev[c1]);
      }
    #pragma omp parallel for
    for (int c0 = 0; c0 < m - 1; c0 += 1)
      for (int c1 = c0 + 1; c1 < m; c1 += 1)
        corr[c0][c1] = 0.;
    #pragma omp parallel for
    for (int c0 = 0; c0 < m - 1; c0 += 1)
      for (int c1 = c0 + 1; c1 < m; c1 += 1) {
        for (int c2 = 0; c2 < n; c2 += 1)
          corr[c0][c1] += (data[c2][c0] * data[c2][c1]);
        corr[c1][c0] = corr[c0][c1];
      }
    corr[m - 1][m - 1] = 1.;
  }

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;
  int m = M;

  /* Variable declaration/allocation. */
  DATA_TYPE float_n;
  POLYBENCH_2D_ARRAY_DECL(data,DATA_TYPE,N,M,n,m);
  POLYBENCH_2D_ARRAY_DECL(corr,DATA_TYPE,M,M,m,m);
  POLYBENCH_1D_ARRAY_DECL(mean,DATA_TYPE,M,m);
  POLYBENCH_1D_ARRAY_DECL(stddev,DATA_TYPE,M,m);

  /* Initialize array(s). */
  init_array (m, n, &float_n, POLYBENCH_ARRAY(data));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_correlation (m, n, float_n,
		      POLYBENCH_ARRAY(data),
		      POLYBENCH_ARRAY(corr),
		      POLYBENCH_ARRAY(mean),
		      POLYBENCH_ARRAY(stddev));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(m, POLYBENCH_ARRAY(corr)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(data);
  POLYBENCH_FREE_ARRAY(corr);
  POLYBENCH_FREE_ARRAY(mean);
  POLYBENCH_FREE_ARRAY(stddev);

  return 0;
}
