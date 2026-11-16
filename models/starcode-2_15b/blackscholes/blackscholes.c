/**
  * ludcmp.c: PARSEC Benchmark Suite  — LU Decomposition
  * Adapted from core/parsec-benchmark/pkgs/apps/ludcmp/src/ludcmp.c
  * (Copyright (c) 2007 Intel Corp. / Princeton University PARSEC Suite)
  */
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

#include <polybench.h>
#include "ludcmp.h"


static void init_array(int m, int n,
                       DATA_TYPE POLYBENCH_2D(A, M, N, m, n)) {
  int i, j;

  for  (i = 0; i < m; i++)
    for  (j = 0; j < n; j++)
      A[i][j] = ((DATA_TYPE) i * j) / m;
}


static void print_array(int m, int n,
                        DATA_TYPE POLYBENCH_2D(A, M, N, m, n)) {
  int i, j;

  for  (i = 0; i < m; i++)
    for  (j = 0; j < n; j++) {
      fprintf(stderr, DATA_PRINTF_MODIFIER, A[i][j]);
      if  ((i * m + j) % 20 == 0)
        fprintf(stderr, "\n");
     }
  fprintf(stderr, "\n");
}


static void kernel_ludcmp(int m, int n,
                          DATA_TYPE POLYBENCH_2D(A, M, N, m, n)) {
  int i, j, k;
  DATA_TYPE sum;

  for  (k = 0; k < _PB_M - 1; k++) {
    for  (i = k + 1; i < _PB_M; i++) {
      A[i][k] /= A[k][k];
      for  (j = k + 1; j < _PB_N; j++)
        A[i][j] -= A[i][k] * A[k][j];
     }
   }
}


int main(int argc, char **argv) {
  int m = M;
  int n = N;

  POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, M, N, m, n);

  init_array(m, n, POLYBENCH_ARRAY(A));

  polybench_start_instruments;

  kernel_ludcmp(m, n, POLYBENCH_ARRAY(A));

  polybench_stop_instruments;
  polybench_print_instruments;

  polybench_prevent_dce(print_array(m, n, POLYBENCH_ARRAY(A)));

  POLYBENCH_FREE_ARRAY(A);

  return 0;
}
