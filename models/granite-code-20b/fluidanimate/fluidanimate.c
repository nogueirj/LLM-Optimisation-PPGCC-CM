/**
 * fluidanimate.c: PARSEC Benchmark Suite — Smoothed Particle Hydrodynamics (SPH) Fluid Simulation
 * Adapted from core/parsec-benchmark/pkgs/apps/fluidanimate/src/serial.cpp
 * (Authors: Richard O. Lee, Christian Bienia, Christian Fensch)
 */
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

#include <polybench.h>
#include "fluidanimate.h"

static void init_array(int nparticles,
                       DATA_TYPE POLYBENCH_1D(px, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(py, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(pz, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(vx, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(vy, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(vz, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(hvx, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(hvy, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(hvz, NPARTICLES, nparticles),
                       DATA_TYPE POLYBENCH_1D(density, NPARTICLES, nparticles)) {
  int i;
  for (i = 0; i < nparticles; i++) {
    px[i] = -0.05 + 0.0025 * (DATA_TYPE)(i % 40);
    py[i] = -0.06 + 0.0025 * (DATA_TYPE)((i / 40) % 40);
    pz[i] = -0.05 + 0.0025 * (DATA_TYPE)((i / 1600) % 40);
    vx[i] = 0.01 * (DATA_TYPE)((i % 7) - 3);
    vy[i] = -0.02 * (DATA_TYPE)(i % 5);
    vz[i] = 0.01 * (DATA_TYPE)((i % 9) - 4);
    hvx[i] = vx[i];
    hvy[i] = vy[i];
    hvz[i] = vz[i];
    density[i] = 1000.0;
  }
}

static void print_array(int nparticles,
                        DATA_TYPE POLYBENCH_1D(px, NPARTICLES, nparticles),
                        DATA_TYPE POLYBENCH_1D(py, NPARTICLES, nparticles),
                        DATA_TYPE POLYBENCH_1D(pz, NPARTICLES, nparticles),
                        DATA_TYPE POLYBENCH_1D(density, NPARTICLES, nparticles)) {
  int i;
  for (i = 0; i < nparticles; i++) {
    fprintf(stderr, DATA_PRINTF_MODIFIER, px[i]);
    fprintf(stderr, DATA_PRINTF_MODIFIER, py[i]);
    fprintf(stderr, DATA_PRINTF_MODIFIER, pz[i]);
    fprintf(stderr, DATA_PRINTF_MODIFIER, density[i]);
    if (i % 5 == 0)
      fprintf(stderr, "\n");
  }
  fprintf(stderr, "\n");
}

static void kernel_fluidanimate(int nparticles, int nframes,
                                DATA_TYPE POLYBENCH_1D(px, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(py, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(pz, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(vx, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(vy, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(vz, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(hvx, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(hvy, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(hvz, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(ax, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(ay, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(az, NPARTICLES, nparticles),
                                DATA_TYPE POLYBENCH_1D(density, NPARTICLES, nparticles)) {
  int fr, i, j;
  DATA_TYPE h = 0.01695;
  DATA_TYPE hSq = h * h;
  DATA_TYPE densityCoeff = 315.0 / (64.0 * 3.14159265358979 * pow(h, 9.0));
  DATA_TYPE pressureCoeff = 45.0 / (3.14159265358979 * pow(h, 6.0));
  DATA_TYPE viscosityCoeff = 18.0 / (3.14159265358979 * pow(h, 6.0));
  DATA_TYPE doubleRestDensity = 2000.0;
  DATA_TYPE timeStep = 0.001;
  DATA_TYPE dx, dy, dz, distSq, t, dist, hmr, fpress, inv_rho;

#pragma scop
#pragma omp parallel for private(i, j, dx, dy, dz, distSq, t, dist, hmr, fpress, inv_rho)
  for (fr = 0; fr < _PB_NFRAMES; fr++) {
    /* Phase 1: SPH Kernel Density Accumulation */
#pragma omp parallel for private(i, j)
    for (i = 0; i < _PB_NPARTICLES; i++) {
      density[i] = hSq * hSq * hSq;
      for (j = 0; j < _PB_NPARTICLES; j++) {
        if (i != j) {
          dx = px[i] - px[j];
          dy = py[i] - py[j];
          dz = pz[i] - pz[j];
          distSq = dx * dx + dy * dy + dz * dz;
          if (distSq < hSq) {
            t = hSq - distSq;
            density[i] += t * t * t;
          }
        }
      }
      density[i] = density[i] * densityCoeff + 1000.0;
    }

    /* Phase 2: SPH Pressure, Viscosity Forces and Wall Collisions */
#pragma omp parallel for private(i, j, dx, dy, dz, distSq, dist, hmr, inv_rho)
    for (i = 0; i < _PB_NPARTICLES; i++) {
      ax[i] = 0.0;
      ay[i] = -9.8;
      az[i] = 0.0;
      for (j = 0; j < _PB_NPARTICLES; j++) {
        if (i != j) {
          dx = px[i] - px[j];
          dy = py[i] - py[j];
          dz = pz[i] - pz[j];
          distSq = dx * dx + dy * dy + dz * dz;
          if (distSq < hSq && distSq > 1.0e-12) {
            dist = sqrt(distSq);
            hmr = h - dist;
            inv_rho = 1.0 / (density[i] * density[j]);
            fpress = pressureCoeff * (hmr * hmr / dist) *
                     (density[i] + density[j] - doubleRestDensity) * inv_rho;
            ax[i] += dx * fpress + (vx[j] - vx[i]) * viscosityCoeff * hmr * inv_rho;
            ay[i] += dy * fpress + (vy[j] - vy[i]) * viscosityCoeff * hmr * inv_rho;
            az[i] += dz * fpress + (vz[j] - vz[i]) * viscosityCoeff * hmr * inv_rho;
          }
        }
      }
    }

    /* Phase 3: Leapfrog Integration (AdvanceParticles) */
#pragma omp parallel for private(i, j)
    for (i = 0; i < _PB_NPARTICLES; i++) {
      hvx[i] = hvx[i] + ax[i] * timeStep;
      hvy[i] = hvy[i] + ay[i] * timeStep;
      hvz[i] = hvz[i] + az[i] * timeStep;
      vx[i] = 0.5 * (vx[i] + hvx[i]);
      vy[i] = 0.5 * (vy[i] + hvy[i]);
      vz[i] = 0.5 * (vz[i] + hvz[i]);
      px[i] = px[i] + hvx[i] * timeStep;
      py[i] = py[i] + hvy[i] * timeStep;
      pz[i] = pz[i] + hvz[i] * timeStep;
    }
  }
#pragma endscop
}

int main(int argc, char **argv) {
  int nparticles = NPARTICLES;
  int nframes = NFRAMES;

  POLYBENCH_1D_ARRAY_DECL(px, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(py, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(pz, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(vx, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(vy, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(vz, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(hvx, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(hvy, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(hvz, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(ax, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(ay, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(az, DATA_TYPE, NPARTICLES, nparticles);
  POLYBENCH_1D_ARRAY_DECL(density, DATA_TYPE, NPARTICLES, nparticles);

  init_array(nparticles, POLYBENCH_ARRAY(px), POLYBENCH_ARRAY(py),
             POLYBENCH_ARRAY(pz), POLYBENCH_ARRAY(vx), POLYBENCH_ARRAY(vy),
             POLYBENCH_ARRAY(vz), POLYBENCH_ARRAY(hvx), POLYBENCH_ARRAY(hvy),
             POLYBENCH_ARRAY(hvz), POLYBENCH_ARRAY(density));

  polybench_start_instruments;

  kernel_fluidanimate(nparticles, nframes,
                      POLYBENCH_ARRAY(px), POLYBENCH_ARRAY(py),
                      POLYBENCH_ARRAY(pz), POLYBENCH_ARRAY(vx),
                      POLYBENCH_ARRAY(vy), POLYBENCH_ARRAY(vz),
                      POLYBENCH_ARRAY(hvx), POLYBENCH_ARRAY(hvy),
                      POLYBENCH_ARRAY(hvz), POLYBENCH_ARRAY(ax),
                      POLYBENCH_ARRAY(ay), POLYBENCH_ARRAY(az),
                      POLYBENCH_ARRAY(density));

  polybench_stop_instruments;
  polybench_print_instruments;

  polybench_prevent_dce(print_array(nparticles, POLYBENCH_ARRAY(px),
                                    POLYBENCH_ARRAY(py), POLYBENCH_ARRAY(pz),
                                    POLYBENCH_ARRAY(density)));

  POLYBENCH_FREE_ARRAY(px);
  POLYBENCH_FREE_ARRAY(py);
  POLYBENCH_FREE_ARRAY(pz);
  POLYBENCH_FREE_ARRAY(vx);
  POLYBENCH_FREE_ARRAY(vy);
  POLYBENCH_FREE_ARRAY(vz);
  POLYBENCH_FREE_ARRAY(hvx);
  POLYBENCH_FREE_ARRAY(hvy);
  POLYBENCH_FREE_ARRAY(hvz);
  POLYBENCH_FREE_ARRAY(ax);
  POLYBENCH_FREE_ARRAY(ay);
  POLYBENCH_FREE_ARRAY(az);
  POLYBENCH_FREE_ARRAY(density);

  return 0;
}
