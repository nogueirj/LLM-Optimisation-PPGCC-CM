#include <stdio.h>
   #include <unistd.h>
   #include <string.h>
   #include <math.h>
   #include <omp.h>

   /* Include polybench common header. */
   #include <polybench.h>

   /* Include benchmark-specific header. */
   /* Default data type is double, default size is 4000. */
   #include "atax.h"

   /* Array initialization. */
   // ... Rest of the code ...

   /* Main computational kernel. The whole function will be timed,
      including the call and return. */
   static
   void kernel_atax(int nx, int ny,
		    DATA_TYPE POLYBENCH_2D(A,NX,NY,nx,ny),
		    DATA_TYPE POLYBENCH_1D(x,NY,ny),
		    DATA_TYPE POLYBENCH_1D(y,NY,ny),
		    DATA_TYPE POLYBENCH_1D(tmp,NX,nx))
   {
     int i, j;

   #pragma scop
   #pragma omp parallel for private(i, j) schedule(static)
     for (i = 0; i < _PB_NX; i++)
     {
       tmp[i] = 0;
       for (j = 0; j < _PB_NY; j++)
         tmp[i] = tmp[i] + A[i][j] * x[j];

       #pragma omp atomic
       for (j = 0; j < _PB_NY; j++)
         y[j] = y[j] + A[i][j] * tmp[i];
     }
   #pragma endscop

   }

   // ... Rest of the code ...
