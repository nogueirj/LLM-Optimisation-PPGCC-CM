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
  
  #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
  #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
  #define ppcg_fdiv_q(n,d) (((n)<0) ? -((-(n)+(d)-1)/(d)) : (n)/(d))
  {
    for (int c0 = 0; c0 < m - 1; c0 += 1)
      corr[c0][c0] = 1.;
    for (int c0 = 0; c0 < m; c0 += 32)
      for (int c1 = 0; c1 <= ppcg_max(0, n - 1); c1 += 32)
        for (int c2 = 0; c2 <= ppcg_min(31, m - c0 - 1); c2 += 1) {
          if (c1 == 0)
            mean[c0 + c2] = 0.;
          for (int c3 = 0; c3 <= ppcg_min(31, n - c1 - 1); c3 += 1)
            mean[c0 + c2] += data[c1 + c3][c0 + c2];
        }
    for (int c0 = 0; c0 < m; c0 += 32)
      for (int c1 = 0; c1 <= ppcg_max(0, n - 1); c1 += 32)
        for (int c2 = 0; c2 <= ppcg_min(31, m - c0 - 1); c2 += 1) {
          if (c1 == 0) {
            stddev[c0 + c2] = 0.;
            mean[c0 + c2] /= float_n;
          }
          for (int c3 = 0; c3 <= ppcg_min(31, n - c1 - 1); c3 += 1)
            stddev[c0 + c2] += ((data[c1 + c3][c0 + c2] - mean[c0 + c2]) * (data[c1 + c3][c0 + c2] - mean[c0 + c2]));
        }
    for (int c0 = 0; c0 < m; c0 += 1) {
      stddev[c0] /= float_n;
      stddev[c0] = sqrt(stddev[c0]);
      stddev[c0] = ((stddev[c0] <= eps) ? 1. : stddev[c0]);
    }
    for (int c0 = 0; c0 < n; c0 += 32)
      for (int c1 = 0; c1 < m; c1 += 32)
        for (int c2 = 0; c2 <= ppcg_min(31, n - c0 - 1); c2 += 1)
          for (int c3 = 0; c3 <= ppcg_min(31, m - c1 - 1); c3 += 1) {
            data[c0 + c2][c1 + c3] -= mean[c1 + c3];
            data[c0 + c2][c1 + c3] /= (sqrt(float_n) * stddev[c1 + c3]);
          }
    for (int c0 = 0; c0 < m - 1; c0 += 32)
      for (int c1 = c0; c1 < m - 1; c1 += 32)
        for (int c2 = 0; c2 <= ppcg_min(31, m - c0 - 2); c2 += 1)
          for (int c3 = ppcg_max(0, c0 - c1 + c2); c3 <= ppcg_min(31, m - c1 - 2); c3 += 1)
            corr[c0 + c2][c1 + c3 + 1] = 0.;
    for (int c0 = 0; c0 < m - 1; c0 += 32)
      for (int c1 = c0; c1 < m; c1 += 32)
        for (int c2 = ppcg_min(0, 32 * n - 32 * ppcg_fdiv_q(31 * n + 31, 32)); c2 <= n; c2 += 32)
          for (int c3 = 0; c3 <= ppcg_min(ppcg_min(31, m - c0 - 2), -c0 + c1 + 30); c3 += 1)
            for (int c4 = ppcg_max(0, c0 - c1 + c3 + 1); c4 <= ppcg_min(31, m - c1 - 1); c4 += 1) {
              for (int c5 = ppcg_max(0, -c2); c5 <= ppcg_min(31, n - c2 - 1); c5 += 1)
                corr[c0 + c3][c1 + c4] += (data[c2 + c5][c0 + c3] * data[c2 + c5][c1 + c4]);
              if (c2 + 31 >= n)
                corr[c1 + c4][c0 + c3] = corr[c0 + c3][c1 + c4];
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
