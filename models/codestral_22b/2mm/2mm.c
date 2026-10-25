#include <stdio.h>
   #include <unistd.h>
   #include <string.h>
   #include <math.h>
   #include <omp.h>

   /* Include polybench common header. */
   #include <polybench.h>

   /* Include benchmark-specific header. */
   /* Default data type is double, default size is 4000. */
   #include "2mm.h"

   /* Array initialization. */
   static void init_array(...) { ... }

   /* DCE code. */
   static void print_array(...) { ... }

   /* Main computational kernel. */
   static void kernel_2mm(...) {
     int i, j, k;

   #pragma omp parallel for private(i, j, k)
     for (i = 0; i < _PB_NI; i++)
       for (j = 0; j < _PB_NJ; j++) {
         tmp[i][j] = 0;
         for (k = 0; k < _PB_NK; ++k)
           tmp[i][j] += alpha * A[i][k] * B[k][j];
       }

   #pragma omp parallel for private(i, j, k)
     for (i = 0; i < _PB_NI; i++)
       for (j = 0; j < _PB_NL; j++) {
         D[i][j] *= beta;
         for (k = 0; k < _PB_NJ; ++k)
           D[i][j] += tmp[i][k] * C[k][j];
       }
   }

   /* Main function. */
   int main(...) { ... }
