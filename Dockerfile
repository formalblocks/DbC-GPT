FROM ubuntu:focal

# Generic packages
RUN apt update && DEBIAN_FRONTEND="noninteractive" apt install -y \
  cmake \
  curl \
  git \
  libboost-filesystem-dev \
  libboost-program-options-dev \
  libboost-system-dev \
  libboost-test-dev \
  python3-pip \
  software-properties-common \
  unzip \
  wget

# Python dependencies
RUN pip3 install psutil

# CVC4
RUN curl --silent "https://api.github.com/repos/CVC4/CVC4/releases/latest" | grep browser_download_url | grep -E 'linux' | cut -d '"' -f 4 | wget -qi - -O /usr/local/bin/cvc4 \
  && chmod a+x /usr/local/bin/cvc4

# Z3
RUN curl --silent "https://api.github.com/repos/Z3Prover/z3/releases/26331124" | grep browser_download_url | grep -E 'ubuntu' | cut -d '"' -f 4 | wget -qi - -O z3.zip \
  && unzip -p z3.zip '*bin/z3' > /usr/local/bin/z3 \
  && chmod a+x /usr/local/bin/z3

# Get .NET
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
  && dpkg -i packages-microsoft-prod.deb \
  && apt update \
  && apt install -y apt-transport-https \
  && apt update \
  && apt install -y dotnet-sdk-3.1

# Get boogie
RUN dotnet tool install --global boogie --version 2.6.17
ENV PATH="${PATH}:/root/.dotnet/tools"

# Get and compile solc-verify
RUN git clone -b 0.5 https://github.com/SRI-CSL/solidity.git \
  && cd solidity \
  && mkdir -p build \
  && cd build \
  && cmake .. -DUSE_Z3=Off -DUSE_CVC4=Off \
  && make \
  && make install

# Get java
RUN apt update && DEBIAN_FRONTEND="noninteractive" apt install -y \
  openjdk-11-jre-headless

# Get node
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&\
  apt install -y nodejs

RUN npm install --global ganache@7.9.2

# Specific version of python
RUN apt install -y python3.9
RUN ln -s /usr/bin/python3.9 /usr/bin/python
RUN ln -sf /usr/bin/python3.9 /usr/bin/python3 

# pip libraries
COPY requirements.txt .
# install requirements but not solc-select (dependency of slither-analyzer)
RUN pip install -r requirements.txt --no-deps

COPY . .
