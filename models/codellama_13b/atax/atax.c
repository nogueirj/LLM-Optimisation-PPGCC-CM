#pragma omp parallel for private(j) schedule(static, 1) collapse(2)
for (i = 0; i < _PB_NY; i++)
{
  for (j = 0; j < _PB_NX; j++)
  {
    tmp[i] = 0;
    for (k = 0; k < _PB_NY; k++)
      tmp[i] = tmp[i] + A[i][k] * x[k];
    y[i] = y[i] + A[i][j] * tmp[i];
  }
}
