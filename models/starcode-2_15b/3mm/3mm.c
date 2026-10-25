#pragma omp parallel for private (k) schedule (dynamic, 50)
  for  (i  =  0;  i  <  _PB_NI;  i++) {
    for  (j  =  0;  j  <  _PB_NJ;  j++)  {
      E[i][j]  =  0;
      for  (k  =  0;  k  <  _PB_NK;  ++k)
        E[i][j]  +=  A[i][k]  *  B[k][j];
     }
  }
#pragma omp parallel for private (k) schedule (dynamic, 50)
  for  (i  =  0;  i  <  _PB_NJ;  i++) {
    for  (j  =  0;  j  <  _PB_NL;  j++) {
      F[i][j]  =  0;
      for  (k  =  0;  k  <  _PB_NM;  ++k)
        F[i][j]  +=  C[i][k]  *  D[k][j];
    }
  }
#pragma omp parallel for private (k) schedule (dynamic, 50)
  for  (i  =  0;  i  <  _PB_NI;  i++) {
    for  (j  =  0;  j  <  _PB_NL;  j++)  {
      G[i][j]  =  0;
      for  (k  =  0;  k  <  _PB_NJ;  ++k)
        G[i][j]  +=  E[i][k]  *  F[k][j];
    }
  }
