#ifndef OP_X_H
# define OP_X_H

# include <polybench.h>

# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(STANDARD_DATASET) && !defined(LARGE_DATASET) && !defined(EXTRALARGE_DATASET)
#  define STANDARD_DATASET
# endif

# if !defined(L1) && !defined(L2) && !defined(L3) && !defined(L4)
#  ifdef MINI_DATASET
#   define L1 32
#   define L2 32
#   define L3 32
#   define L4 32
#  endif

#  ifdef SMALL_DATASET
#   define L1 128
#   define L2 128
#   define L3 128
#   define L4 128
#  endif

#  ifdef STANDARD_DATASET
#   define L1 1024
#   define L2 1024
#   define L3 1024
#   define L4 1024
#  endif

#  ifdef LARGE_DATASET
#   define L1 2000
#   define L2 2000
#   define L3 2000
#   define L4 2000
#  endif

#  ifdef EXTRALARGE_DATASET
#   define L1 4000
#   define L2 4000
#   define L3 4000
#   define L4 4000
#  endif
# endif

# define _LIM_1 POLYBENCH_LOOP_BOUND(L1, d1)
# define _LIM_2 POLYBENCH_LOOP_BOUND(L2, d2)
# define _LIM_3 POLYBENCH_LOOP_BOUND(L3, d3)
# define _LIM_4 POLYBENCH_LOOP_BOUND(L4, d4)

# ifndef REAL_T
#  define REAL_T double
#  define FMT_REAL "%0.2lf "
# endif

# define BUF_2D(var, D1, D2, d1, d2) POLYBENCH_2D(var, D1, D2, d1, d2)
# define ALLOC_BUF_2D(var, type, D1, D2, d1, d2) POLYBENCH_2D_ARRAY_DECL(var, type, D1, D2, d1, d2)
# define BUF_PTR(var) POLYBENCH_ARRAY(var)
# define FREE_BUF(var) POLYBENCH_FREE_ARRAY(var)
# define TIMER_START polybench_start_instruments
# define TIMER_STOP polybench_stop_instruments
# define TIMER_PRINT polybench_print_instruments
# define KEEP_LIVE(call) polybench_prevent_dce(call)

#endif
