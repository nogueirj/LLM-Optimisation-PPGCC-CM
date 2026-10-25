/* E := A*B */
#pragma omp parallel for private(i) shared(E, A, B) schedule(static)
for (i = 0; i < _PB_NI; i++)
  for (j = 0; j < _PB_NJ; j++) {
    E[i][j] = 0;
    for (k = 0; k < _PB_NK; ++k)
      E[i][j] += A[i][k] * B[k][j];
  }

/* F := C*D */
#pragma omp parallel for private(i) shared(F, C, D) schedule(static)
for (i = 0; i < _PB_NJ; i++)
  for (j = 0; j < _PB_NL; j++) {
    F[i][j] = 0;
    for (k = 0; k < _PB_NM; ++k)
      F[i][j] += C[i][k] * D[k][j];
  }

/* G := E*F */
#pragma omp parallel for private(i) shared(G, E, F) schedule(static)
for (i = 0; i < _PB_NI; i++)
  for (j = 0; j < _PB_NL; j++) {
    G[i][j] = 0;
    for (k = 0; k < _PB_NJ; ++k)
      G[i][j] += E[i][k] * F[k][j];
  }
