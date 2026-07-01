# DawnCC Compiler - Versão Compatível Ubuntu 16.04 + LLVM 3.8
# Especificação oficial do DawnCC

FROM --platform=linux/amd64 ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive \
    LLVM_VER=3.7.0 \
    ROOT=/opt/dawncc

ENV DAWN_PATH=${ROOT}/DawnCC \
    LLVM_SRC=${ROOT}/llvm \
    LLVM_BUILD=${ROOT}/llvm-build \
    PATH=${ROOT}/llvm-build/bin:${PATH} \
    LD_LIBRARY_PATH=${ROOT}/llvm-build/lib

# g++-5 é obrigatório — DawnCC não compila com g++-6+
RUN apt-get update && apt-get install -y \
    build-essential g++-5 gcc-5 cmake \
    wget unzip xz-utils python \
    libedit-dev libxml2-dev zlib1g-dev \
    && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 50 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-5 50 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR ${ROOT}

# Download — build.sh usa llvm.org/releases, que redireciona para releases.llvm.org
RUN wget -q https://releases.llvm.org/${LLVM_VER}/llvm-${LLVM_VER}.src.tar.xz \
    && wget -q https://releases.llvm.org/${LLVM_VER}/cfe-${LLVM_VER}.src.tar.xz \
    && wget -q -O DawnCC-Compiler-master.zip \
         https://github.com/gleisonsdm/DawnCC-Compiler/archive/master.zip

# Extração com --strip 1, exatamente como no build.sh oficial
RUN mkdir ${LLVM_SRC} \
    && tar -Jxf llvm-${LLVM_VER}.src.tar.xz -C ${LLVM_SRC} --strip 1 \
    && mkdir ${LLVM_SRC}/tools/clang \
    && tar -Jxf cfe-${LLVM_VER}.src.tar.xz -C ${LLVM_SRC}/tools/clang --strip 1 \
    && unzip -q DawnCC-Compiler-master.zip \
    && mv DawnCC-Compiler-master ${DAWN_PATH} \
    && rm -f *.tar.xz *.zip

# Aplicar patch do DawnCC no LLVM
RUN cd ${LLVM_SRC} && patch -p1 < ${DAWN_PATH}/ArrayInference/llvm-patch.diff

# Setup do ScopeFinder como Clang extra tool — reproduz exatamente o build.sh:
#   mkdir -p extra/, cria CMakeLists.txt, copia scope-finder/
RUN mkdir -p ${LLVM_SRC}/tools/clang/tools/extra \
    && echo "add_subdirectory(scope-finder)" \
         > ${LLVM_SRC}/tools/clang/tools/extra/CMakeLists.txt \
    && cp -rf ${DAWN_PATH}/ScopeFinder/scope-finder \
              ${LLVM_SRC}/tools/clang/tools/extra/

# Build LLVM + Clang 3.7
# build.sh: debug + shared libs; pre-build clang antes do make geral (workaround)
# LLVM_TARGETS_TO_BUILD=X86 reduz o tempo de build; remova para compilar todos os targets
RUN mkdir ${LLVM_BUILD} && cd ${LLVM_BUILD} \
    && CXX=g++-5 cmake \
         -DCMAKE_BUILD_TYPE=debug \
         -DBUILD_SHARED_LIBS=ON \
         -DLLVM_TARGETS_TO_BUILD=X86 \
         ${LLVM_SRC} \
    && make clang -j$(nproc) \
    && make -j$(nproc)

# Build dos passes do DawnCC (executado de dentro de lib/, apontando para ../)
RUN mkdir ${DAWN_PATH}/lib && cd ${DAWN_PATH}/lib \
    && CXX=g++-5 cmake -DLLVM_DIR=${LLVM_BUILD}/share/llvm/cmake ../ \
    && make -j$(nproc)

# PrivateDetector é buildado separadamente, em libPrivate/ (como no build.sh)
RUN mkdir ${ROOT}/libPrivate && cd ${ROOT}/libPrivate \
    && CXX=g++-5 cmake -DLLVM_DIR=${LLVM_BUILD}/share/llvm/cmake \
         ${DAWN_PATH}/PrivateDetector \
    && make -j$(nproc)

WORKDIR /workspace
CMD ["/bin/bash"]