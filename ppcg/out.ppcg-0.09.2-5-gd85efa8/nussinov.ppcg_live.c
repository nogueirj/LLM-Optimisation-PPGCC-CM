/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* nussinov.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "nussinov.h"

/* RNA bases represented as chars, range is [0,3] */
typedef char base;

#define match(b1, b2) (((b1)+(b2)) == 3 ? 1 : 0)
#define max_score(s1, s2) ((s1 >= s2) ? s1 : s2)

/* Array initialization. */
static
void init_array (int n,
                 base POLYBENCH_1D(seq,N,n),
		 DATA_TYPE POLYBENCH_2D(table,N,N,n,n))
{
  int i, j;

  //base is AGCT/0..3
  for (i=0; i <n; i++) {
     seq[i] = (base)((i+1)%4);
  }

  for (i=0; i <n; i++)
     for (j=0; j <n; j++)
       table[i][j] = 0;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int n,
		 DATA_TYPE POLYBENCH_2D(table,N,N,n,n))

{
  int i, j;
  int t = 0;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("table");
  for (i = 0; i < n; i++) {
    for (j = i; j < n; j++) {
      if (t % 20 == 0) fprintf (POLYBENCH_DUMP_TARGET, "\n");
      fprintf (POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, table[i][j]);
      t++;
    }
  }
  POLYBENCH_DUMP_END("table");
  POLYBENCH_DUMP_FINISH;
}


/* Main computational kernel. The whole function will be timed,
   including the call and return. */
/*
  Original version by Dave Wonnacott at Haverford College <davew@cs.haverford.edu>,
  with help from Allison Lake, Ting Zhou, and Tian Jin,
  based on algorithm by Nussinov, described in Allison Lake's senior thesis.
*/
static
void kernel_nussinov(int n, base POLYBENCH_1D(seq,N,n),
			   DATA_TYPE POLYBENCH_2D(table,N,N,n,n))
{
  int i, j, k;

 /* ppcg generated CPU code */
 
 #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
 #define ppcg_max(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x > _y ? _x : _y; })
 for (int c0 = 0; c0 < n - 1; c0 += 32)
   for (int c1 = ppcg_max(0, -((n - c0 - 1) % 32) + n - c0 - 33); c1 < n - 1; c1 += 32)
     for (int c2 = ppcg_max(0, n - c0 - c1 - 33); c2 <= ppcg_min(31, n - c0 - 2); c2 += 1)
       for (int c3 = ppcg_max(0, n - c0 - c1 - c2 - 2); c3 <= ppcg_min(31, n - c1 - 2); c3 += 1) {
         table[n - c0 - c2 - 2][c1 + c3 + 1] = ((table[n - c0 - c2 - 2][c1 + c3 + 1] >= table[n - c0 - c2 - 2][c1 + c3]) ? table[n - c0 - c2 - 2][c1 + c3 + 1] : table[n - c0 - c2 - 2][c1 + c3]);
         table[n - c0 - c2 - 2][c1 + c3 + 1] = ((table[n - c0 - c2 - 2][c1 + c3 + 1] >= table[n - c0 - c2 - 1][c1 + c3 + 1]) ? table[n - c0 - c2 - 2][c1 + c3 + 1] : table[n - c0 - c2 - 1][c1 + c3 + 1]);
         if (c0 + c1 + c2 + c3 + 1 >= n)
           table[n - c0 - c2 - 2][c1 + c3 + 1] = ((table[n - c0 - c2 - 2][c1 + c3 + 1] >= (table[n - c0 - c2 - 1][c1 + c3] + (((seq[n - c0 - c2 - 2] + seq[c1 + c3 + 1]) == 3) ? 1 : 0))) ? table[n - c0 - c2 - 2][c1 + c3 + 1] : (table[n - c0 - c2 - 1][c1 + c3] + (((seq[n - c0 - c2 - 2] + seq[c1 + c3 + 1]) == 3) ? 1 : 0)));
         for (int c4 = n - c0 - c2 - 1; c4 <= c1 + c3; c4 += 1)
           table[n - c0 - c2 - 2][c1 + c3 + 1] = ((table[n - c0 - c2 - 2][c1 + c3 + 1] >= (table[n - c0 - c2 - 2][c4] + table[c4 + 1][c1 + c3 + 1])) ? table[n - c0 - c2 - 2][c1 + c3 + 1] : (table[n - c0 - c2 - 2][c4] + table[c4 + 1][c1 + c3 + 1]));
         if (c0 + c1 + c2 + c3 + 2 == n)
           table[n - c0 - c2 - 2][n - c0 - c2 - 1] = ((table[n - c0 - c2 - 2][n - c0 - c2 - 1] >= table[n - c0 - c2 - 1][n - c0 - c2 - 2]) ? table[n - c0 - c2 - 2][n - c0 - c2 - 1] : table[n - c0 - c2 - 1][n - c0 - c2 - 2]);
       }

}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int n = N;

  /* Variable declaration/allocation. */
  POLYBENCH_1D_ARRAY_DECL(seq, base, N, n);
  POLYBENCH_2D_ARRAY_DECL(table, DATA_TYPE, N, N, n, n);

  /* Initialize array(s). */
  init_array (n, POLYBENCH_ARRAY(seq), POLYBENCH_ARRAY(table));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_nussinov (n, POLYBENCH_ARRAY(seq), POLYBENCH_ARRAY(table));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(n, POLYBENCH_ARRAY(table)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(seq);
  POLYBENCH_FREE_ARRAY(table);

  return 0;
}
