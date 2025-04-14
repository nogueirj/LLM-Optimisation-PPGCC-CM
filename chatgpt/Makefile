
all: seq omp collapse

seq: gemm/gemm.c gemm/gemm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I gemm ../polybench-c-3.2/utilities/polybench.c gemm/gemm.c -lm -o gemm-seq.exe

omp: gemm/gemm-omp.c gemm/gemm.h

	gcc -O2 -I ../polybench-c-3.2/utilities -I gemm ../polybench-c-3.2/utilities/polybench.c gemm/gemm-omp.c -lm -fopenmp -o gemm-omp.exe

collapse: gemm/gemm-omp-collapse.c gemm/gemm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I gemm ../polybench-c-3.2/utilities/polybench.c gemm/gemm-omp-collapse.c -lm -fopenmp -o gemm-omp-collapse.exe

clean:
	rm *.exe
