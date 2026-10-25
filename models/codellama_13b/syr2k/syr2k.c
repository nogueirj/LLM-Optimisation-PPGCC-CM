#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>

/* Declare the BLAS function dgemm */
void dgemm(const char* transa, const char* transb,
           int m, int n, int k,
           double alpha, const double* a, int lda,
           const double* b, int ldb,
           double beta, double* c, int ldc);

int main()
{
    int m = 1000;
    int n = 1000;
    int k = 1000;
    double alpha = 1.0;
    double beta = 0.0;
    double *a = malloc(m * k * sizeof(double));
    double *b = malloc(k * n * sizeof(double));
    double *c = malloc(m * n * sizeof(double));

    /* Initialize arrays */
    for (int i = 0; i < m * k; i++) {
        a[i] = (double)rand() / RAND_MAX;
    }
    for (int i = 0; i < k * n; i++) {
        b[i] = (double)rand() / RAND_MAX;
    }
    for (int i = 0; i < m * n; i++) {
        c[i] = 0.0;
    }

    /* Perform the matrix multiplication using BLAS */
    #pragma omp parallel for
    for (int i = 0; i < m; i++) {
        #pragma omp parallel for simd
        for (int j = 0; j < n; j++) {
            double sum = 0.0;
            for (int k = 0; k < k; k++) {
                sum += a[i * k + k] * b[k * n + j];
            }
            c[i * n + j] += alpha * sum + beta * c[i * n + j];
        }
    }

    /* Print the resulting matrix */
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            printf("%.1f ", c[i * n + j]);
        }
        printf("\n");
    }

    return 0;
}
