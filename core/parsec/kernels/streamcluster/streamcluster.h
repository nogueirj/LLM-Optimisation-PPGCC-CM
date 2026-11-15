/**
 * streamcluster.h: PARSEC Benchmark Suite — Online k-Median Stream Clustering
 * Adapted from core/parsec-benchmark/pkgs/kernels/streamcluster/src/streamcluster.cpp
 */
#ifndef _STREAMCLUSTER_H
# define _STREAMCLUSTER_H

/* Default to STANDARD_DATASET (PARSEC simlarge equivalent). */
# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
#  define STANDARD_DATASET
# endif

# if !defined(NPOINTS) && !defined(NDIM)
#  ifdef MINI_DATASET
#   define NPOINTS 256
#   define NDIM 32
#   define NITER 16
#  endif

#  ifdef SMALL_DATASET
#   define NPOINTS 512
#   define NDIM 32
#   define NITER 32
#  endif

#  ifdef STANDARD_DATASET /* PARSEC simlarge */
#   define NPOINTS 16384
#   define NDIM 128
#   define NITER 256
#  endif

#  ifdef LARGE_DATASET /* PARSEC native */
#   define NPOINTS 32768
#   define NDIM 128
#   define NITER 512
#  endif

#  ifdef EXTRALARGE_DATASET
#   define NPOINTS 65536
#   define NDIM 128
#   define NITER 512
#  endif
# endif /* !NPOINTS */

# define _PB_NPOINTS POLYBENCH_LOOP_BOUND(NPOINTS,npoints)
# define _PB_NDIM POLYBENCH_LOOP_BOUND(NDIM,ndim)
# define _PB_NITER POLYBENCH_LOOP_BOUND(NITER,niter)

# ifndef DATA_TYPE
#  define DATA_TYPE double
#  define DATA_PRINTF_MODIFIER "%0.6lf "
# endif

#endif /* !_STREAMCLUSTER_H */
