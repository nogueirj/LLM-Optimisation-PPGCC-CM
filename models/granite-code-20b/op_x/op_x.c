#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include "op_x.h"

static void setup_buffers(int d1, int d2, int d3, int d4,
                          REAL_T *k1, REAL_T *k2,
                          REAL_T BUF_2D(src_p, L1, L3, d1, d3),
                          REAL_T BUF_2D(src_q, L3, L2, d3, d2),
                          REAL_T BUF_2D(src_r, L2, L4, d2, d4),
                          REAL_T BUF_2D(dst_u, L1, L4, d1, d4)) {
  int u, v;

  *k1 = 32412;
  *k2 = 2123;
  for (u = 0; u < d1; u++)
    for (v = 0; v < d3; v++)
      src_p[u][v] = ((REAL_T)u * v) / d1;
  for (u = 0; u < d3; u++)
    for (v = 0; v < d2; v++)
      src_q[u][v] = ((REAL_T)u * (v + 1)) / d2;
  for (u = 0; u < d2; u++)
    for (v = 0; v < d4; v++)
      src_r[u][v] = ((REAL_T)u * (v + 3)) / d4;
  for (u = 0; u < d1; u++)
    for (v = 0; v < d4; v++)
      dst_u[u][v] = ((REAL_T)u * (v + 2)) / d3;
}

static void emit_result(int d1, int d4,
                        REAL_T BUF_2D(dst_u, L1, L4, d1, d4)) {
  int u, v;

  for (u = 0; u < d1; u++)
    for (v = 0; v < d4; v++) {
      fprintf(stderr, FMT_REAL, dst_u[u][v]);
      if ((u * d1 + v) % 20 == 0)
        fprintf(stderr, "\n");
    }
  fprintf(stderr, "\n");
}

static void compute_pipeline(int d1, int d2, int d3, int d4,
                             REAL_T k1, REAL_T k2,
                             REAL_T BUF_2D(buf_m, L1, L2, d1, d2),
                             REAL_T BUF_2D(src_p, L1, L3, d1, d3),
                             REAL_T BUF_2D(src_q, L3, L2, d3, d2),
                             REAL_T BUF_2D(src_r, L2, L4, d2, d4),
                             REAL_T BUF_2D(dst_u, L1, L4, d1, d4)) {
  int u, v, w;

  for (u = 0; u < _LIM_1; u++)
    for (v = 0; v < _LIM_2; v++) {
      buf_m[u][v] = 0;
      for (w = 0; w < _LIM_3; ++w)
        buf_m[u][v] += k1 * src_p[u][w] * src_q[w][v];
    }
  #pragma omp parallel for schedule(static) collapse(2) default(none) shared(k1,src_p,src_q,src_r,dst_u) private(u,v,w) firstprivate(d1,d2,d3,d4)
  for (u = 0; u < _LIM_1; u++)
    for (v = 0; v < _LIM_4; v++) {
      dst_u[u][v] *= k2;
      #pragma omp simd
      for (w = 0; w < _LIM_2; ++w)
        dst_u[u][v] += buf_m[u][w] * src_r[w][v];
    }
}

int main(int argc, char **argv) {
  int d1 = L1;
  int d2 = L2;
  int d3 = L3;
  int d4 = L4;

  REAL_T k1;
  REAL_T k2;
  ALLOC_BUF_2D(buf_m, REAL_T, L1, L2, d1, d2);
  ALLOC_BUF_2D(src_p, REAL_T, L1, L3, d1, d3);
  ALLOC_BUF_2D(src_q, REAL_T, L3, L2, d3, d2);
  ALLOC_BUF_2D(src_r, REAL_T, L2, L4, d2, d4);
  ALLOC_BUF_2D(dst_u, REAL_T, L1, L4, d1, d4);

  setup_buffers(d1, d2, d3, d4, &k1, &k2, BUF_PTR(src_p),
                BUF_PTR(src_q), BUF_PTR(src_r), BUF_PTR(dst_u));

  TIMER_START;

  compute_pipeline(d1, d2, d3, d4, k1, k2, BUF_PTR(buf_m),
                   BUF_PTR(src_p), BUF_PTR(src_q), BUF_PTR(src_r),
                   BUF_PTR(dst_u));

  TIMER_STOP;
  TIMER_PRINT;

  KEEP_LIVE(emit_result(d1, d4, BUF_PTR(dst_u)));

  FREE_BUF(buf_m);
  FREE_BUF(src_p);
  FREE_BUF(src_q);
  FREE_BUF(src_r);
  FREE_BUF(dst_u);

  return 0;
}
