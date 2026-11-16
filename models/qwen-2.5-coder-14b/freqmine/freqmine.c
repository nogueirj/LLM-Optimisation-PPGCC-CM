/**
 * freqmine.c: PARSEC Benchmark Suite — FP-Growth Frequent Itemset Mining
 * Adapted from core/parsec-benchmark/pkgs/apps/freqmine/src/fp_tree.cpp
 * (Author: Jianfei Zhu, Concordia University / PARSEC Suite)
 */
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

#include <polybench.h>
#include "freqmine.h"

static void init_array(int ntrans, int nitems, int tlen,
                       int POLYBENCH_2D(transactions, NTRANS, TLEN, ntrans, tlen),
                       DATA_TYPE POLYBENCH_1D(trans_weight, NTRANS, ntrans),
                       int POLYBENCH_1D(ntype, NTRANS, ntrans),
                       DATA_TYPE POLYBENCH_2D(cond_supp, NITEMS, NITEMS, nitems, nitems),
                       DATA_TYPE POLYBENCH_1D(pattern_score, NITEMS, nitems),
                       int POLYBENCH_1D(freq_count, NITEMS, nitems)) {
  int t, k, i, j;
  for (t = 0; t < ntrans; t++) {
    trans_weight[t] = 1.0 + 0.1 * (DATA_TYPE)(t % 10);
    ntype[t] = 0;
    for (k = 0; k < tlen; k++) {
      transactions[t][k] = (t * 13 + k * 7 + (t / 16)) % nitems;
    }
  }
  for (i = 0; i < nitems; i++) {
    pattern_score[i] = 0.0;
    freq_count[i] = 0;
    for (j = 0; j < nitems; j++) {
      cond_supp[i][j] = 0.0;
    }
  }
}

static void print_array(int nitems,
                        DATA_TYPE POLYBENCH_1D(pattern_score, NITEMS, nitems),
                        int POLYBENCH_1D(freq_count, NITEMS, nitems)) {
  int i;
  for (i = 0; i < nitems; i++) {
    fprintf(stderr, DATA_PRINTF_MODIFIER, pattern_score[i]);
    fprintf(stderr, "%d ", freq_count[i]);
    if (i % 10 == 0)
      fprintf(stderr, "\n");
  }
  fprintf(stderr, "\n");
}

static void kernel_freqmine(int ntrans, int nitems, int tlen,
                            int POLYBENCH_2D(transactions, NTRANS, TLEN, ntrans, tlen),
                            DATA_TYPE POLYBENCH_1D(trans_weight, NTRANS, ntrans),
                            int POLYBENCH_1D(ntype, NTRANS, ntrans),
                            DATA_TYPE POLYBENCH_2D(cond_supp, NITEMS, NITEMS, nitems, nitems),
                            DATA_TYPE POLYBENCH_1D(pattern_score, NITEMS, nitems),
                            int POLYBENCH_1D(freq_count, NITEMS, nitems)) {
  int t, k, item, j, v, mask, has_item, count;
  DATA_TYPE threshold, score, w;

#pragma scop
  /* Phase 1: Database Tiling — Hot-Item Bitmask Prefix Extraction */
#pragma omp parallel for private(t, k, mask)
  for (t = 0; t < _PB_NTRANS; t++) {
    mask = 0;
    for (k = 0; k < _PB_TLEN; k++) {
      v = transactions[t][k];
      if (v < 16) {
        mask |= (1 << v);
      }
    }
    ntype[t] = mask;
  }

  /* Phase 2: FP-Growth Conditional Pattern Base Support Mining */
  threshold = (DATA_TYPE)_PB_NTRANS * 0.02;
#pragma omp parallel for private(item, j, cond_supp[item], score, count)
  for (item = 0; item < _PB_NITEMS; item++) {
    for (j = 0; j < _PB_NITEMS; j++) {
      cond_supp[item][j] = 0.0;
    }

    for (t = 0; t < _PB_NTRANS; t++) {
      has_item = 0;
      for (k = 0; k < _PB_TLEN; k++) {
        if (transactions[t][k] == item) {
          has_item = 1;
        }
      }
      if (has_item) {
        w = trans_weight[t] * (1.0 + 0.001 * (DATA_TYPE)(ntype[t] & 0xff));
        for (k = 0; k < _PB_TLEN; k++) {
          v = transactions[t][k];
          if (v < item) {
            cond_supp[item][v] += w;
          }
        }
      }
    }

    score = 0.0;
    count = 0;
    for (j = 0; j < item; j++) {
      if (cond_supp[item][j] >= threshold) {
        score += cond_supp[item][j];
        count++;
      }
    }
    pattern_score[item] = score;
    freq_count[item] = count;
  }
#pragma endscop
}

int main(int argc, char **argv) {
  int ntrans = NTRANS;
  int nitems = NITEMS;
  int tlen = TLEN;

  POLYBENCH_2D_ARRAY_DECL(transactions, int, NTRANS, TLEN, ntrans, tlen);
  POLYBENCH_1D_ARRAY_DECL(trans_weight, DATA_TYPE, NTRANS, ntrans);
  POLYBENCH_1D_ARRAY_DECL(ntype, int, NTRANS, ntrans);
  POLYBENCH_2D_ARRAY_DECL(cond_supp, DATA_TYPE, NITEMS, NITEMS, nitems, nitems);
  POLYBENCH_1D_ARRAY_DECL(pattern_score, DATA_TYPE, NITEMS, nitems);
  POLYBENCH_1D_ARRAY_DECL(freq_count, int, NITEMS, nitems);

  init_array(ntrans, nitems, tlen,
             POLYBENCH_ARRAY(transactions), POLYBENCH_ARRAY(trans_weight),
             POLYBENCH_ARRAY(ntype), POLYBENCH_ARRAY(cond_supp),
             POLYBENCH_ARRAY(pattern_score), POLYBENCH_ARRAY(freq_count));

  polybench_start_instruments;

  kernel_freqmine(ntrans, nitems, tlen,
                  POLYBENCH_ARRAY(transactions), POLYBENCH_ARRAY(trans_weight),
                  POLYBENCH_ARRAY(ntype), POLYBENCH_ARRAY(cond_supp),
                  POLYBENCH_ARRAY(pattern_score), POLYBENCH_ARRAY(freq_count));

  polybench_stop_instruments;
  polybench_print_instruments;

  polybench_prevent_dce(print_array(nitems, POLYBENCH_ARRAY(pattern_score),
                                    POLYBENCH_ARRAY(freq_count)));

  POLYBENCH_FREE_ARRAY(transactions);
  POLYBENCH_FREE_ARRAY(trans_weight);
  POLYBENCH_FREE_ARRAY(ntype);
  POLYBENCH_FREE_ARRAY(cond_supp);
  POLYBENCH_FREE_ARRAY(pattern_score);
  POLYBENCH_FREE_ARRAY(freq_count);

  return 0;
}
