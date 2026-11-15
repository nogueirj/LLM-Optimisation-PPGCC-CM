/**
 * freqmine.h: PARSEC Benchmark Suite — FP-Growth Frequent Itemset Mining
 * Adapted from core/parsec-benchmark/pkgs/apps/freqmine/src/fp_tree.cpp
 */
#ifndef _FREQMINE_H
# define _FREQMINE_H

/* Default to STANDARD_DATASET (PARSEC simlarge equivalent). */
# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
#  define STANDARD_DATASET
# endif

# if !defined(NTRANS) && !defined(NITEMS)
#  ifdef MINI_DATASET
#   define NTRANS 256
#   define NITEMS 32
#   define TLEN 16
#  endif

#  ifdef SMALL_DATASET
#   define NTRANS 512
#   define NITEMS 64
#   define TLEN 16
#  endif

#  ifdef STANDARD_DATASET /* PARSEC simlarge */
#   define NTRANS 32768
#   define NITEMS 512
#   define TLEN 64
#  endif

#  ifdef LARGE_DATASET /* PARSEC native */
#   define NTRANS 65536
#   define NITEMS 1024
#   define TLEN 64
#  endif

#  ifdef EXTRALARGE_DATASET
#   define NTRANS 32768
#   define NITEMS 512
#   define TLEN 32
#  endif
# endif /* !NTRANS */

# define _PB_NTRANS POLYBENCH_LOOP_BOUND(NTRANS,ntrans)
# define _PB_NITEMS POLYBENCH_LOOP_BOUND(NITEMS,nitems)
# define _PB_TLEN POLYBENCH_LOOP_BOUND(TLEN,tlen)

# ifndef DATA_TYPE
#  define DATA_TYPE double
#  define DATA_PRINTF_MODIFIER "%0.6lf "
# endif

#endif /* !_FREQMINE_H */
