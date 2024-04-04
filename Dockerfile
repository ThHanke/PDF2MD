# # Stage 1: Builder/Compiler
# FROM docker.io/python:3.9-slim as builder

# RUN apt update && \
#     apt install --no-install-recommends -y build-essential gcc
# COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Stage 2: Runtime
FROM pytorch/pytorch:2.1.2-cuda11.8-cudnn8-runtime
ADD . /src
WORKDIR /src
ENV DEBIAN_FRONTEND noninteractive
ENV TZ=Europe/Berlin
RUN buildDeps='locales curl wget build-essential software-properties-common' \
    && set -x \
    && apt-get update && apt-get install -y $buildDeps --no-install-recommends \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && sed -i 's/^# de_DE.UTF-8 UTF-8$/de_DE.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen en_US.UTF-8 de_DE.UTF-8 \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && apt clean && rm -rf /var/lib/apt/lists/*
# COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/dist-packages

RUN buildDeps='libmagic1 libxml2' \
    && set -x \
    && apt-get update && apt-get install -y $buildDeps --no-install-recommends \
    && apt clean && rm -rf /var/lib/apt/lists/*

#Run export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
#libjpeg-dev libpng-dev libtiff-dev zlib1g-dev ocrmypdf tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu

ARG gversion=10.03.0
#install ghostscript
RUN wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10030/ghostscript-$gversion.tar.gz && \
    tar -xzf ghostscript-$gversion.tar.gz && \
    cd ghostscript-$gversion && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf ghostscript-$gversion && \
    rm ghostscript-$gversion.tar.gz


#install tesseract 5
RUN apt-get install -y apt-transport-https && \
    add-apt-repository ppa:alex-p/tesseract-ocr5 && \
    apt-get update -oAcquire::AllowInsecureRepositories=true
RUN apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

#install requirements - remember conda is installed in that image
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#run a initial test - models will be downladed aswell
# RUN python ./marker/convert_single.py ./tests/science_article.pdf ./output/science_article.md


ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "6","--proxy-headers"]