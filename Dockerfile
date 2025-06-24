FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-runtime AS base
ENV DEBIAN_FRONTEND noninteractive
ENV TZ=Europe/Berlin
RUN buildDeps='locales curl wget build-essential software-properties-common libmagic1 libxml2 git ocrmypdf' \
    && set -x \
    && apt-get update && apt-get install -y $buildDeps --no-install-recommends \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && sed -i 's/^# de_DE.UTF-8 UTF-8$/de_DE.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen en_US.UTF-8 de_DE.UTF-8 \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && apt clean && rm -rf /var/lib/apt/lists/*

#install ghostscript
# ARG gversion=10.03.0
# RUN wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10030/ghostscript-$gversion.tar.gz && \
#     tar -xzf ghostscript-$gversion.tar.gz && \
#     cd ghostscript-$gversion && \
#     ./configure && \
#     make && \
#     make install && \
#     cd .. && \
#     rm -rf ghostscript-$gversion && \
#     rm ghostscript-$gversion.tar.gz

FROM base
#install tesseract 5
# RUN apt-get install -y apt-transport-https && \
#     add-apt-repository ppa:alex-p/tesseract-ocr5 && \
#     apt update --quiet
RUN apt install -y tesseract-ocr tesseract-ocr-eng
#tesseract-ocr-eng tesseract-ocr-deu

# RUN git clone https://github.com/VikParuchuri/marker.git ../marker
# COPY marker_setup.py /marker/setup.py
# RUN cd /marker && \
#     pip install .

#install requirements - remember conda is installed in that image
ADD ./requirements.txt /src/requirements.txt
WORKDIR /src
RUN pip install --no-cache-dir --upgrade -r requirements.txt

ADD . /src

#run a initial test - models will be downladed aswell
# RUN python ./marker/convert_single.py ./tests/science_article.pdf ./output/science_article.md

ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

#ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "6","--proxy-headers"]
ENTRYPOINT ["python", "app.py"]
