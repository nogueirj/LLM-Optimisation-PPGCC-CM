/**
 * swaptions.h: PARSEC Benchmark Suite — Heath-Jarrow-Morton (HJM) Swaption Pricing
 * Adapted from core/parsec-benchmark/pkgs/apps/swaptions/src/HJM_Securities.cpp
 */
#ifndef _SWAPTIONS_H
# define _SWAPTIONS_H

/* Default to STANDARD_DATASET (PARSEC simlarge equivalent). */
# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
#  define STANDARD_DATASET
# endif

# if !defined(NSWAPTIONS) && !defined(NTRIALS)
#  ifdef MINI_DATASET
#   define NSWAPTIONS 32
#   define NTRIALS 128
#   define NSTEPS 11
#   define NFACTORS 3
#  endif

#  ifdef SMALL_DATASET
#   define NSWAPTIONS 64
#   define NTRIALS 256
#   define NSTEPS 11
#   define NFACTORS 3
#  endif

#  ifdef STANDARD_DATASET /* PARSEC simlarge */
#   define NSWAPTIONS 512
#   define NTRIALS 4096
#   define NSTEPS 11
#   define NFACTORS 3
#  endif

#  ifdef LARGE_DATASET /* PARSEC native */
#   define NSWAPTIONS 1024
#   define NTRIALS 8192
#   define NSTEPS 11
#   define NFACTORS 3
#  endif

#  ifdef EXTRALARGE_DATASET
#   define NSWAPTIONS 2048
#   define NTRIALS 16384
#   define NSTEPS 11
#   define NFACTORS 3
#  endif
# endif /* !NSWAPTIONS */

# define _PB_NSWAPTIONS POLYBENCH_LOOP_BOUND(NSWAPTIONS,nswaptions)
# define _PB_NTRIALS POLYBENCH_LOOP_BOUND(NTRIALS,ntrials)
# define _PB_NSTEPS POLYBENCH_LOOP_BOUND(NSTEPS,nsteps)
# define _PB_NFACTORS POLYBENCH_LOOP_BOUND(NFACTORS,nfactors)

# ifndef DATA_TYPE
#  define DATA_TYPE double
#  define DATA_PRINTF_MODIFIER "%0.6lf "
# endif

#endif /* !_SWAPTIONS_H */
