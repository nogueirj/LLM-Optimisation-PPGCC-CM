#include <omp.h>

...

/* Initialize variables. */
int i, j, k;
int num_threads = omp_get_num_threads();
int tid = omp_get_thread_num();

/* E := A*B */
#pragma omp parallel for private(i, j, k) schedule(static) collapse(2)
for (i = 0; i < _PB_NI; i++) {
  for (j = 0; j < _PB_NJ; j++) {
    E[i][j] = 0;
    for (k = 0; k < _PB_NK; ++k) {
      E[i][j] += A[i][k] * B[k][j];
    }
  }
}

/* F := C*D */
#pragma omp parallel for private(i, j, k) schedule(static) collapse(2)
for (i = 0; i < _PB_NJ; i++) {
  for (j = 0; j < _PB_NL; j++) {
    F[i][j] = 0;
    for (k = 0; k < _PB_NM; ++k) {
      F[i][j] += C[i][k] * D[k][j];
    }
  }
}

/* G := E*F */
#pragma omp parallel for private(i, j, k) schedule(static) collapse(2)
for (i = 0; i < _PB_NI; i++) {
  for (j = 0; j < _PB_NL; j++) {
    G[i][j] = 0;
    for (k = 0; k < _PB_NJ; ++k) {
      G[i][j] += E[i][k] * F[k][j];
    }
  }
}
