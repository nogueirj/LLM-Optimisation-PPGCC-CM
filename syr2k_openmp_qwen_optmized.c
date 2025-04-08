#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
/* Default data type is double, default size is 4000. */
#include "syr2k.h"

/* Array initialization. */
static
void init_array(int ni, int nj,
        DATA_TYPE *alpha,
        DATA_TYPE *beta,
        DATA_TYPE POLYBENCH_2D(C,NI,NI,ni,ni),
        DATA_TYPE POLYBENCH_2D(A,NI,NJ,ni,nj),
        DATA_TYPE POLYBENCH_2D(B,NI,NJ,ni,nj))
{
  int i, j;

  *alpha = 32412;
  *beta = 2123;
  for (i = 0; i < ni; i++)
    for (j = 0; j < nj; j++) {
      A[i][j] = ((DATA_TYPE) i*j) / ni;
      B[i][j] = ((DATA_TYPE) i*j) / ni;
    }
  for (i = 0; i < ni; i++)
    for (j = 0; j < ni; j++)
      C[i][j] = ((DATA_TYPE) i*j) / ni;
}

/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int ni,
         DATA_TYPE POLYBENCH_2D(C,NI,NI,ni,ni))
{
  int i, j;

  for (i = 0; i < ni; i++)
    for (j = 0; j < ni; j++) {
    fprintf (stderr, DATA_PRINTF_MODIFIER, C[i][j]);
    if ((i * ni + j) % 20 == 0) fprintf (stderr, "\n");
    }
  fprintf (stderr, "\n");
}

/* Main computational kernel. The whole function will be timed,
   including the call and return. */
static
void kernel_syr2k(int ni, int nj,
          DATA_TYPE alpha,
          DATA_TYPE beta,
          DATA_TYPE POLYBENCH_2D(C,NI,NI,ni,ni),
          DATA_TYPE POLYBENCH_2D(A,NI,NJ,ni,nj),
          DATA_TYPE POLYBENCH_2D(B,NI,NJ,ni,nj))
{
  int i, j, k;

#pragma omp parallel for collapse(2)
  for (i = 0; i < ni; i++)
    for (j = 0; j < ni; j++)
      C[i][j] *= beta;

#pragma omp parallel for collapse(3)
  for (i = 0; i < ni; i++)
    for (j = 0; j < ni; j++)
      for (k = 0; k < nj; k++) {
        C[i][j] += alpha * A[i][k] * B[k][j];
        C[j][i] += alpha * B[j][k] * A[k][i];
      }
}

int main()
{
  int ni = NI, nj = NJ;
  DATA_TYPE alpha, beta;
  DATA_TYPE POLYBENCH_2D(C,NI,NI,ni,ni);
  DATA_TYPE POLYBENCH_2D(A,NI,NJ,ni,nj);
  DATA_TYPE POLYBENCH_2D(B,NI,NJ,ni,nj);

  init_array(ni, nj, &alpha, &beta, C, A, B);

  kernel_syr2k(ni, nj, alpha, beta, C, A, B);

  print_array(ni, C);

  return 0;
}