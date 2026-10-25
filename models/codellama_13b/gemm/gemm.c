void kernel_gemm(int ni, int nj, int nk,
		 DATA_TYPE alpha,
		 DATA_TYPE beta,
		 DATA_TYPE POLYBENCH_2D(C,NI,NJ,ni,nj),
		 DATA_TYPE POLYBENCH_2D(A,NI,NK,ni,nk),
		 DATA_TYPE POLYBENCH_2D(B,NK,NJ,nk,nj))
{
#pragma omp parallel for collapse(2) default(none) shared(A,B,C) private(i,j,k)
  for (i = 0; i < ni; i++)
    for (j = 0; j < nj; j++)
      {
	C[i][j] *= beta;
	for (k = 0; k < nk; ++k)
	  C[i][j] += alpha * A[i][k] * B[k][j];
      }
}
