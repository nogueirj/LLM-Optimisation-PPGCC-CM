/**
 * streamcluster.c: PARSEC Benchmark Suite — Online k-Median Stream Clustering
 * Adapted from core/parsec-benchmark/pkgs/kernels/streamcluster/src/streamcluster.cpp
 * (Authors: Jia Deng, Gilberto Contreras, Princeton University)
 */
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

#include <polybench.h>
#include "streamcluster.h"

static void init_array(int npoints, int ndim, int niter,
                       DATA_TYPE POLYBENCH_2D(points, NPOINTS, NDIM, npoints, ndim),
                       DATA_TYPE POLYBENCH_1D(weight, NPOINTS, npoints),
                       int POLYBENCH_1D(feasible, NITER, niter),
                       DATA_TYPE POLYBENCH_1D(cost, NPOINTS, npoints),
                       int POLYBENCH_1D(assign, NPOINTS, npoints)) {
  int i, d;
  for (i = 0; i < npoints; i++) {
    weight[i] = 1.0 + 0.05 * (DATA_TYPE)(i % 20);
    cost[i] = 0.0;
    assign[i] = 0;
    for (d = 0; d < ndim; d++) {
      points[i][d] = ((DATA_TYPE)(((i + 1) * (d + 3) * 31 + i * i * 7 + d * 17) % 1009)) / 1009.0;
    }
  }
  for (i = 0; i < niter; i++) {
    feasible[i] = (i * 97 + 13) % npoints;
  }
}

static void print_array(int npoints,
                        DATA_TYPE POLYBENCH_1D(cost, NPOINTS, npoints),
                        int POLYBENCH_1D(assign, NPOINTS, npoints)) {
  int i;
  for (i = 0; i < npoints; i++) {
    fprintf(stderr, DATA_PRINTF_MODIFIER, cost[i]);
    fprintf(stderr, "%d ", assign[i]);
    if (i % 10 == 0)
      fprintf(stderr, "\n");
  }
  fprintf(stderr, "\n");
}

static void kernel_streamcluster(int npoints, int ndim, int niter,
                                 DATA_TYPE POLYBENCH_2D(points, NPOINTS, NDIM, npoints, ndim),
                                 DATA_TYPE POLYBENCH_1D(weight, NPOINTS, npoints),
                                 int POLYBENCH_1D(feasible, NITER, niter),
                                 DATA_TYPE POLYBENCH_1D(cost, NPOINTS, npoints),
                                 int POLYBENCH_1D(assign, NPOINTS, npoints)) {
  int i, d, step, x;
  DATA_TYPE dist, diff, x_cost;

#pragma scop
  /* Initial facility center assignment (pspeedy / CenterCreate) */
  #pragma omp parallel for private(i, d, dist, diff) firstprivate(_PB_NPOINTS, _PB_NDIM)
for (i = 0; i < _PB_NPOINTS; i++) {
    dist = 0.0;
    for (d = 0; d < _PB_NDIM; d++) {
      diff = points[i][d] - points[0][d];
      dist += diff * diff;
    }
    cost[i] = dist * weight[i];
    assign[i] = 0;
  }

  /* Online local search over candidate facilities (pFL / pgain) */
  for (step = 0; step < _PB_NITER; step++) {
    x = feasible[step];
    #pragma omp parallel for private(i, d, dist, diff, x_cost) firstprivate(_PB_NPOINTS, _PB_NDIM)
for (i = 0; i < _PB_NPOINTS; i++) {
      dist = 0.0;
      for (d = 0; d < _PB_NDIM; d++) {
        diff = points[i][d] - points[x][d];
        dist += diff * diff;
      }
      x_cost = dist * weight[i];
      if (x_cost < cost[i]) {
        cost[i] = x_cost;
        assign[i] = x;
      }
    }
  }
#pragma endscop
}

int main(int argc, char **argv) {
  int npoints = NPOINTS;
  int ndim = NDIM;
  int niter = NITER;

  POLYBENCH_2D_ARRAY_DECL(points, DATA_TYPE, NPOINTS, NDIM, npoints, ndim);
  POLYBENCH_1D_ARRAY_DECL(weight, DATA_TYPE, NPOINTS, npoints);
  POLYBENCH_1D_ARRAY_DECL(feasible, int, NITER, niter);
  POLYBENCH_1D_ARRAY_DECL(cost, DATA_TYPE, NPOINTS, npoints);
  POLYBENCH_1D_ARRAY_DECL(assign, int, NPOINTS, npoints);

  init_array(npoints, ndim, niter,
             POLYBENCH_ARRAY(points), POLYBENCH_ARRAY(weight),
             POLYBENCH_ARRAY(feasible), POLYBENCH_ARRAY(cost),
             POLYBENCH_ARRAY(assign));

  polybench_start_instruments;

  kernel_streamcluster(npoints, ndim, niter,
                       POLYBENCH_ARRAY(points), POLYBENCH_ARRAY(weight),
                       POLYBENCH_ARRAY(feasible), POLYBENCH_ARRAY(cost),
                       POLYBENCH_ARRAY(assign));

  polybench_stop_instruments;
  polybench_print_instruments;

  polybench_prevent_dce(print_array(npoints, POLYBENCH_ARRAY(cost),
                                    POLYBENCH_ARRAY(assign)));

  POLYBENCH_FREE_ARRAY(points);
  POLYBENCH_FREE_ARRAY(weight);
  POLYBENCH_FREE_ARRAY(feasible);
  POLYBENCH_FREE_ARRAY(cost);
  POLYBENCH_FREE_ARRAY(assign);

  return 0;
}
