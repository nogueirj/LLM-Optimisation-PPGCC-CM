all: 2mmseq 2mmcodellama 3mmseq 3mmcodellama ataxseq ataxcodellama gemmseq gemmcodellama syr2kseq syr2kcodellama 

2mmseq: 2mm/2mm.c 2mm/2mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 2mm ../polybench-c-3.2/utilities/polybench.c 2mm/2mm.c -lm -o 2mm-seq.exe

2mmcodellama: 2mm/2mm_openmp_codellama_optmized.c 2mm/2mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 2mm ../polybench-c-3.2/utilities/polybench.c 2mm/2mm_openmp_codellama_optmized.c -lm -fopenmp -o 2mm-codellama.exe

3mmseq: 3mm/3mm.c 3mm/3mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 3mm ../polybench-c-3.2/utilities/polybench.c 3mm/3mm.c -lm -o 3mm-seq.exe

3mmcodellama: 3mm/3mm_openmp_codellama_optmized.c 3mm/3mm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I 3mm ../polybench-c-3.2/utilities/polybench.c 3mm/3mm_openmp_codellama_optmized.c -lm -fopenmp -o 3mm-codellama.exe

ataxseq: atax/atax.c atax/atax.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I atax ../polybench-c-3.2/utilities/polybench.c atax/atax.c -lm -o atax-seq.exe

ataxcodellama: atax/atax_openmp_codellama_optmized.c atax/atax.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I atax ../polybench-c-3.2/utilities/polybench.c atax/atax_openmp_codellama_optmized.c -lm -fopenmp -o atax-codellama.exe


gemmseq: gemm/gemm.c gemm/gemm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I gemm ../polybench-c-3.2/utilities/polybench.c gemm/gemm.c -lm -o gemm-seq.exe

gemmcodellama: gemm/gemm_openmp_codellama_optmized.c gemm/gemm.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I gemm ../polybench-c-3.2/utilities/polybench.c gemm/gemm_openmp_codellama_optmized.c -lm -fopenmp -o gemm-codellama.exe


syr2kseq: syr2k/syr2k.c syr2k/syr2k.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I syr2k ../polybench-c-3.2/utilities/polybench.c syr2k/syr2k.c -lm -o syr2k-seq.exe

syr2kcodellama: syr2k/syr2k_openmp_codellama_optmized.c syr2k/syr2k.h
	gcc -O2 -I ../polybench-c-3.2/utilities -I syr2k ../polybench-c-3.2/utilities/polybench.c syr2k/syr2k_openmp_codellama_optmized.c -lm -fopenmp -o syr2k-codellama.exe

clean:
	rm *.exe
