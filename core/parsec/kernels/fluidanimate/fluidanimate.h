/**
 * fluidanimate.h: PARSEC Benchmark Suite — Smoothed Particle Hydrodynamics (SPH) Fluid Simulation
 * Adapted from core/parsec-benchmark/pkgs/apps/fluidanimate/src/serial.cpp
 */
#ifndef _FLUIDANIMATE_H
# define _FLUIDANIMATE_H

/* Default to STANDARD_DATASET (PARSEC simlarge equivalent). */
# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
#  define STANDARD_DATASET
# endif

# if !defined(NPARTICLES) && !defined(NFRAMES)
#  ifdef MINI_DATASET
#   define NPARTICLES 256
#   define NFRAMES 2
#  endif

#  ifdef SMALL_DATASET
#   define NPARTICLES 512
#   define NFRAMES 3
#  endif

#  ifdef STANDARD_DATASET /* PARSEC simlarge */
#   define NPARTICLES 4096
#   define NFRAMES 5
#  endif

#  ifdef LARGE_DATASET /* PARSEC native */
#   define NPARTICLES 8192
#   define NFRAMES 5
#  endif

#  ifdef EXTRALARGE_DATASET
#   define NPARTICLES 16384
#   define NFRAMES 5
#  endif
# endif /* !NPARTICLES */

# define _PB_NPARTICLES POLYBENCH_LOOP_BOUND(NPARTICLES,nparticles)
# define _PB_NFRAMES POLYBENCH_LOOP_BOUND(NFRAMES,nframes)

# ifndef DATA_TYPE
#  define DATA_TYPE double
#  define DATA_PRINTF_MODIFIER "%0.6lf "
# endif

#endif /* !_FLUIDANIMATE_H */
