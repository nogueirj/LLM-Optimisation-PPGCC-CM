all: 2mmseq 2mmcodestral 3mmseq 3mmcodestral ataxseq ataxcodestral gemmseq gemmcodestral syr2kseq syr2kcodestral 

2mmseq: 2mm/2mm.c 2mm/2mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 2mm ../polybench-c-3.2/utilities/polybench.c 2mm/2mm.c -lm -o 2mm-seq.exe

2mmcodestral: 2mm/2mm_openmp_codestral_optmized.c 2mm/2mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 2mm ../polybench-c-3.2/utilities/polybench.c 2mm/2mm_openmp_codestral_optmized.c -lm -fopenmp -o 2mm-codestral.exe

3mmseq: 3mm/3mm.c 3mm/3mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 3mm ../polybench-c-3.2/utilities/polybench.c 3mm/3mm.c -lm -o 3mm-seq.exe

3mmcodestral: 3mm/3mm_openmp_codestral_optmized.c 3mm/3mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 3mm ../polybench-c-3.2/utilities/polybench.c 3mm/3mm_openmp_codestral_optmized.c -lm -fopenmp -o 3mm-codestral.exe

ataxseq: atax/atax.c atax/atax.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I atax ../polybench-c-3.2/utilities/polybench.c atax/atax.c -lm -o atax-seq.exe

ataxcodestral: atax/atax_openmp_codestral_optmized.c atax/atax.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I atax ../polybench-c-3.2/utilities/polybench.c atax/atax_openmp_codestral_optmized.c -lm -fopenmp -o atax-codestral.exe


gemmseq: gemm/gemm.c gemm/gemm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I gemm ../polybench-c-3.2/utilities/polybench.c gemm/gemm.c -lm -o gemm-seq.exe

gemmcodestral: gemm/gemm_openmp_codestral_optmized.c gemm/gemm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I gemm ../polybench-c-3.2/utilities/polybench.c gemm/gemm_openmp_codestral_optmized.c -lm -fopenmp -o gemm-codestral.exe


syr2kseq: syr2k/syr2k.c syr2k/syr2k.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I syr2k ../polybench-c-3.2/utilities/polybench.c syr2k/syr2k.c -lm -o syr2k-seq.exe

syr2kcodestral: syr2k/syr2k_openmp_codestral_optmized.c syr2k/syr2k.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I syr2k ../polybench-c-3.2/utilities/polybench.c syr2k/syr2k_openmp_codestral_optmized.c -lm -fopenmp -o syr2k-codestral.exe

clean:
	rm *.exe
