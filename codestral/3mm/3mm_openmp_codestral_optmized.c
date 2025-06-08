#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>

/* Include polybench common header. */
#include "polybench.h"

/* Include benchmark-specific header. */
#include "3mm.h"
#include <omp.h>  // Inclusão da biblioteca OpenMP

/* Array initialization. */
static
void init_array(int ni, int nj, int nk, int nl, int nm,
                DATA_TYPE *alpha,
                DATA_TYPE *beta,
                DATA_TYPE POLYBENCH_2D(A, NI, NK, ni, nk),
                DATA_TYPE POLYBENCH_2D(B, NK, NJ, nk, nj),
                DATA_TYPE POLYBENCH_2D(C, NL, NM, nl, nm),
                DATA_TYPE POLYBENCH_2D(D, NJ, NM, nj, nm))
{
    int i, j;

    *alpha = (DATA_TYPE) random();
    *beta = (DATA_TYPE) random();
    for (i = 0; i < ni; i++)
        for (j = 0; j < nk; j++)
            A[i][j] = ((DATA_TYPE) i*j + 2) / (ni * nk);
    for (i = 0; i < nk; i++)
        for (j = 0; j < nj; j++)
            B[i][j] = ((DATA_TYPE) i*j - 1) / (nk * nj);
    for (i = 0; i < nl; i++)
        for (j = 0; j < nm; j++)
            C[i][j] = ((DATA_TYPE) i*j + 3) / (nl * nm);
    for (i = 0; i < nj; i++)
        for (j = 0; j < nm; j++)
            D[i][j] = ((DATA_TYPE) i*j - 5) / (nj * nm);
}

/* Main computation function. */
static
void kernel_3mm(int ni, int nj, int nk, int nl, int nm,
               DATA_TYPE alpha,
               DATA_TYPE beta,
               DATA_TYPE POLYBENCH_2D(E, NI, NL, ni, nl),
               DATA_TYPE POLYBENCH_2D(F, NL, NJ, nl, nj),
               DATA_TYPE POLYBENCH_2D(G, NI, NM, ni, nm),
               DATA_TYPE POLYBENCH_2D(A, NI, NK, ni, nk),
               DATA_TYPE POLYBENCH_2D(B, NK, NJ, nk, nj),
               DATA_TYPE POLYBENCH_2D(C, NL, NM, nl, nm),
               DATA_TYPE POLYBENCH_2D(D, NJ, NM, nj, nm))
{
    int i, j, k;

#pragma omp parallel for private(i, j, k)
    for (i = 0; i < _PB_NI; i++)
        for (j = 0; j < _PB_NL; j++) {
            E[i][j] = 0;
            for (k = 0; k < _PB_NK; ++k)
                E[i][j] += alpha * A[i][k] * B[k][j];
        }

#pragma omp parallel for private(i, j, k)
    for (i = 0; i < _PB_NL; i++)
        for (j = 0; j < _PB_NJ; j++) {
            F[i][j] = 0;
            for (k = 0; k < _PB_NM; ++k)
                F[i][j] += E[i][k] * D[k][j];
        }

#pragma omp parallel for private(i, j, k)
    for (i = 0; i < _PB_NI; i++)
        for (j = 0; j < _PB_NM; j++) {
            G[i][j] = 0;
            for (k = 0; k < _PB_NJ; ++k)
                G[i][j] += F[i][k] * C[k][j];
        }

#pragma omp parallel for private(i, j)
    for (i = 0; i < _PB_NI; i++)
        for (j = 0; j < _PB_NM; j++)
            G[i][j] *= beta;
}

int main()
{
    /* Register polybench variables. */
    int ni = NI, nj = NJ, nk = NK, nl = NL, nm = NM;
    DATA_TYPE alpha;
    DATA_TYPE beta;
    POLYBENCH_2D_ARRAY_DECL(E, DATA_TYPE, NI, NL, ni, nl);
    POLYBENCH_2D_ARRAY_DECL(F, DATA_TYPE, NL, NJ, nl, nj);
    POLYBENCH_2D_ARRAY_DECL(G, DATA_TYPE, NI, NM, ni, nm);
    POLYBENCH_2D_ARRAY_DECL(A, DATA_TYPE, NI, NK, ni, nk);
    POLYBENCH_2D_ARRAY_DECL(B, DATA_TYPE, NK, NJ, nk, nj);
    POLYBENCH_2D_ARRAY_DECL(C, DATA_TYPE, NL, NM, nl, nm);
    POLYBENCH_2D_ARRAY_DECL(D, DATA_TYPE, NJ, NM, nj, nm);

    /* Allocate memory. */
    polybench_alloc_data(NI, NL, &E[0][0], &F[0][0], &G[0][0], &A[0][0], &B[0][0], &C[0][0], &D[0][0]);

    /* Initialize array. */
    init_array(ni, nj, nk, nl, nm, &alpha, &beta, A, B, C, D);

    /* Start timer. */
    polybench_start_instruments;

    /* Run kernel. */
    kernel_3d_convolution<DATA_TYPE>(ni, nj, nk, nl, nm, alpha, beta, E, F, G, A, B, C, D);

    /* Stop and print timer. */
    polybench_stop_instruments;
    polybench_print_instruments;

    /* Prevent dead-code elimination. All live-out data must be printed
       by the function call in argument. */
    polybench_prevent_dce(print_array4);

    /* Be clean. */
    polybench_free_data(E, F, G, A, B, C, D);

    return 0;
}