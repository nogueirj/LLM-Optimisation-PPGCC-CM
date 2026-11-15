/**
 * blackscholes.h: PARSEC Benchmark Suite — Black-Scholes PDE Option Pricing
 * Adapted from core/parsec-benchmark/pkgs/apps/blackscholes/src/blackscholes.c
 */
#ifndef _BLACKSCHOLES_H
# define _BLACKSCHOLES_H

/* Default to STANDARD_DATASET (PARSEC simlarge equivalent). */
# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
#  define STANDARD_DATASET
# endif

# if !defined(NOPT) && !defined(NRUNS)
#  ifdef MINI_DATASET
#   define NOPT 512
#   define NRUNS 10
#  endif

#  ifdef SMALL_DATASET
#   define NOPT 2048
#   define NRUNS 25
#  endif

#  ifdef STANDARD_DATASET /* PARSEC simlarge */
#   define NOPT 65536
#   define NRUNS 400
#  endif

#  ifdef LARGE_DATASET /* PARSEC native */
#   define NOPT 262144
#   define NRUNS 400
#  endif

#  ifdef EXTRALARGE_DATASET
#   define NOPT 1048576
#   define NRUNS 400
#  endif
# endif /* !NOPT */

# define _PB_NOPT POLYBENCH_LOOP_BOUND(NOPT,nopt)
# define _PB_NRUNS POLYBENCH_LOOP_BOUND(NRUNS,nruns)

# ifndef DATA_TYPE
#  define DATA_TYPE double
#  define DATA_PRINTF_MODIFIER "%0.6lf "
# endif

#endif /* !_BLACKSCHOLES_H */
