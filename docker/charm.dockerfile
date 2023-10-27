FROM gcc:13-bookworm

WORKDIR /app

ARG JOBS
ARG GMP_VER=5.1.3 PBC_VER=0.5.14 PYTHON_VER=3.10.13 CHARM_COMMIT_HASH=07dd2145

# Charm requires GMP 5.x, which is too old for various software sources
RUN curl -O https://gmplib.org/download/gmp/gmp-${GMP_VER}.tar.xz \
  && tar xf gmp-${GMP_VER}.tar.xz \
  && cd gmp-${GMP_VER} \
  && ./configure --prefix=/usr \
  && make -j ${JOBS} \
  && make check -j ${JOBS} \
  && make install \
  && rm -rf /app && mkdir /app && cd /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends flex bison \
  && rm -rf /var/lib/apt/lists/*

# Latest PBC
RUN curl -O https://crypto.stanford.edu/pbc/files/pbc-${PBC_VER}.tar.gz \
  && tar xf pbc-${PBC_VER}.tar.gz \
  && cd pbc-${PBC_VER} \
  && ./configure --prefix=/usr \
  && make -j ${JOBS} \
  && make install \
  && rm -rf /app && mkdir /app && cd /app

# Python 3.11 in Debian software source (apt) can not work (`#include <longintrepr.h>` fails).
# It seems that Python 3.11 introduces some C ABI changes.
# Python 3.10 works fine.
RUN curl -O https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz \
  && tar xf Python-${PYTHON_VER}.tgz \
  && cd Python-${PYTHON_VER} \
  && ./configure --enable-optimizations \
  && make -j ${JOBS} \
  && make install \
  && rm -rf /app && mkdir /app && cd /app

# Latest Charm.
# OpenSSL 1.1 works fine (so no need for 1.0) but 3 seems not to work.
RUN apt-get update \
  && apt-get install -y --no-install-recommends git \
  && git clone https://github.com/JHUISI/charm.git \
  && rm -rf /var/lib/apt/lists/* \
  && cd charm \
  && git checkout ${CHARM_COMMIT_HASH} \
  && ./configure.sh --prefix=/usr \
  && make -j ${JOBS} \
  && make install \
  && rm -rf /app && mkdir /app && cd /app

# The `gcc` base image includes various development tools like `curl` and `xz`, which are helpful.
# If you want a smaller image, copy libraries and headers from this image.
