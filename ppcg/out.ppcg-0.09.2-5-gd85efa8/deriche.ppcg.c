/**
 * This version is stamped on May 10, 2016
 *
 * Contact:
 *   Louis-Noel Pouchet <pouchet.ohio-state.edu>
 *   Tomofumi Yuki <tomofumi.yuki.fr>
 *
 * Web address: http://polybench.sourceforge.net
 */
/* deriche.c: this file is part of PolyBench/C */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include <polybench.h>

/* Include benchmark-specific header. */
#include "deriche.h"


/* Array initialization. */
static
void init_array (int w, int h, DATA_TYPE* alpha,
		 DATA_TYPE POLYBENCH_2D(imgIn,W,H,w,h),
		 DATA_TYPE POLYBENCH_2D(imgOut,W,H,w,h))
{
  int i, j;

  *alpha=0.25; //parameter of the filter

  //input should be between 0 and 1 (grayscale image pixel)
  for (i = 0; i < w; i++)
     for (j = 0; j < h; j++)
	imgIn[i][j] = (DATA_TYPE) ((313*i+991*j)%65536) / 65535.0f;
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int w, int h,
		 DATA_TYPE POLYBENCH_2D(imgOut,W,H,w,h))

{
  int i, j;

  POLYBENCH_DUMP_START;
  POLYBENCH_DUMP_BEGIN("imgOut");
  for (i = 0; i < w; i++)
    for (j = 0; j < h; j++) {
      if ((i * h + j) % 20 == 0) fprintf(POLYBENCH_DUMP_TARGET, "\n");
      fprintf(POLYBENCH_DUMP_TARGET, DATA_PRINTF_MODIFIER, imgOut[i][j]);
    }
  POLYBENCH_DUMP_END("imgOut");
  POLYBENCH_DUMP_FINISH;
}



/* Main computational kernel. The whole function will be timed,
   including the call and return. */
/* Original code provided by Gael Deest */
static
void kernel_deriche(int w, int h, DATA_TYPE alpha,
       DATA_TYPE POLYBENCH_2D(imgIn, W, H, w, h),
       DATA_TYPE POLYBENCH_2D(imgOut, W, H, w, h),
       DATA_TYPE POLYBENCH_2D(y1, W, H, w, h),
       DATA_TYPE POLYBENCH_2D(y2, W, H, w, h)) {
    int i,j;
    DATA_TYPE xm1, tm1, ym1, ym2;
    DATA_TYPE xp1, xp2;
    DATA_TYPE tp1, tp2;
    DATA_TYPE yp1, yp2;

    DATA_TYPE k;
    DATA_TYPE a1, a2, a3, a4, a5, a6, a7, a8;
    DATA_TYPE b1, b2, c1, c2;

   /* ppcg generated CPU code */
   
   #define ppcg_min(x,y)    ({ __typeof__(x) _x = (x); __typeof__(y) _y = (y); _x < _y ? _x : _y; })
   {
     k = (((1.F - expf(-alpha)) * (1.F - expf(-alpha))) / ((1.F + ((2.F * alpha) * expf(-alpha))) - expf(2.F * alpha)));
     b1 = powf(2.F, -alpha);
     if (h >= 1 && w >= 1)
       a1 = (a5 = k);
     b2 = (-expf((-2.F) * alpha));
     a3 = (a7 = ((k * expf(-alpha)) * (alpha + 1.F)));
     a4 = (a8 = ((-k) * expf((-2.F) * alpha)));
     a2 = (a6 = ((k * expf(-alpha)) * (alpha - 1.F)));
     if (h >= 1) {
       for (int c0 = 0; c0 < w; c0 += 1) {
         ym1 = 0.F;
         yp1 = 0.F;
         xp1 = 0.F;
         ym2 = 0.F;
         xp2 = 0.F;
         yp2 = 0.F;
         xm1 = 0.F;
         for (int c1_0 = 0; c1_0 <= h; c1_0 += 1) {
           if (c1_0 >= 1) {
             y2[c0][h - c1_0] = ((((a3 * xp1) + (a4 * xp2)) + (b1 * yp1)) + (b2 * yp2));
             if (h >= c1_0 + 1) {
               xp2 = xp1;
               xp1 = imgIn[c0][h - c1_0];
               yp2 = yp1;
               yp1 = y2[c0][h - c1_0];
             }
           }
           if (h >= c1_0 + 1) {
             y1[c0][c1_0] = ((((a1 * imgIn[c0][c1_0]) + (a2 * xm1)) + (b1 * ym1)) + (b2 * ym2));
             if (h >= c1_0 + 2) {
               xm1 = imgIn[c0][c1_0];
               ym2 = ym1;
               ym1 = y1[c0][c1_0];
             }
           }
         }
       }
       if (w >= 1)
         c1 = (c2 = 1);
     }
     for (int c0 = 0; c0 < w; c0 += 32)
       for (int c1_0 = 0; c1_0 < h; c1_0 += 32)
         for (int c2_0 = 0; c2_0 <= ppcg_min(31, w - c0 - 1); c2_0 += 1)
           for (int c3 = 0; c3 <= ppcg_min(31, h - c1_0 - 1); c3 += 1)
             imgOut[c0 + c2_0][c1_0 + c3] = (c1 * (y1[c0 + c2_0][c1_0 + c3] + y2[c0 + c2_0][c1_0 + c3]));
     if (w >= 1) {
       for (int c0 = 0; c0 < h; c0 += 1) {
         tp1 = 0.F;
         yp1 = 0.F;
         yp2 = 0.F;
         tp2 = 0.F;
         for (int c1_0 = 1; c1_0 <= w; c1_0 += 1) {
           y2[w - c1_0][c0] = ((((a7 * tp1) + (a8 * tp2)) + (b1 * yp1)) + (b2 * yp2));
           if (w >= c1_0 + 1) {
             tp2 = tp1;
             tp1 = imgOut[w - c1_0][c0];
             yp2 = yp1;
             yp1 = y2[w - c1_0][c0];
           }
         }
       }
       for (int c0 = 0; c0 < h; c0 += 1) {
         ym1 = 0.F;
         ym2 = 0.F;
         tm1 = 0.F;
         for (int c1_0 = 0; c1_0 < w; c1_0 += 1) {
           y1[c1_0][c0] = ((((a5 * imgOut[c1_0][c0]) + (a6 * tm1)) + (b1 * ym1)) + (b2 * ym2));
           if (w >= c1_0 + 2) {
             ym2 = ym1;
             ym1 = y1[c1_0][c0];
             tm1 = imgOut[c1_0][c0];
           }
         }
       }
     }
     for (int c0 = 0; c0 < w; c0 += 32)
       for (int c1_0 = 0; c1_0 < h; c1_0 += 32)
         for (int c2_0 = 0; c2_0 <= ppcg_min(31, w - c0 - 1); c2_0 += 1)
           for (int c3 = 0; c3 <= ppcg_min(31, h - c1_0 - 1); c3 += 1)
             imgOut[c0 + c2_0][c1_0 + c3] = (c2 * (y1[c0 + c2_0][c1_0 + c3] + y2[c0 + c2_0][c1_0 + c3]));
   }
}


int main(int argc, char** argv)
{
  /* Retrieve problem size. */
  int w = W;
  int h = H;

  /* Variable declaration/allocation. */
  DATA_TYPE alpha;
  POLYBENCH_2D_ARRAY_DECL(imgIn, DATA_TYPE, W, H, w, h);
  POLYBENCH_2D_ARRAY_DECL(imgOut, DATA_TYPE, W, H, w, h);
  POLYBENCH_2D_ARRAY_DECL(y1, DATA_TYPE, W, H, w, h);
  POLYBENCH_2D_ARRAY_DECL(y2, DATA_TYPE, W, H, w, h);


  /* Initialize array(s). */
  init_array (w, h, &alpha, POLYBENCH_ARRAY(imgIn), POLYBENCH_ARRAY(imgOut));

  /* Start timer. */
  polybench_start_instruments;

  /* Run kernel. */
  kernel_deriche (w, h, alpha, POLYBENCH_ARRAY(imgIn), POLYBENCH_ARRAY(imgOut), POLYBENCH_ARRAY(y1), POLYBENCH_ARRAY(y2));

  /* Stop and print timer. */
  polybench_stop_instruments;
  polybench_print_instruments;

  /* Prevent dead-code elimination. All live-out data must be printed
     by the function call in argument. */
  polybench_prevent_dce(print_array(w, h, POLYBENCH_ARRAY(imgOut)));

  /* Be clean. */
  POLYBENCH_FREE_ARRAY(imgIn);
  POLYBENCH_FREE_ARRAY(imgOut);
  POLYBENCH_FREE_ARRAY(y1);
  POLYBENCH_FREE_ARRAY(y2);

  return 0;
}
