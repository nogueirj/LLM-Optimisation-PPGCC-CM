#pragma omp parallel for
    for  (i  =  0 ;  i  <  _PB_NI  ;  i++ )
      #pragma omp parallel for
      for  (j  =  0 ;  j  <  _PB_NJ  ;  j++ ) {
        C[i][j]  *=  beta ;
        #pragma omp parallel for
        for  (k  =  0 ;  k  <  _PB_NK ;  ++k )
          C[i][j]  +=  alpha  *  A[i][k]  *  B[k][j] ;
      }
