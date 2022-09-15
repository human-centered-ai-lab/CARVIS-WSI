FROM ubuntu:latest AS builder

LABEL maintainer="stefan.baumann@medunigraz.at"

RUN apt-get update -y && apt-get upgrade -y \ 
    && apt-get install meson ninja-build wget -y

RUN wget https://www.cairographics.org/releases/pixman-0.40.0.tar.gz \
    && tar -xf pixman-0.40.0.tar.gz \
    && cd pixman-0.40.0/ \
    && mkdir build && cd build \
    && meson --prefix=/usr --buildtype=release \
    && ninja \
    && ninja test \
    && ninja install    


FROM python:latest

LABEL maintainer="stefan.baumann@medunigraz.at"
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && apt-get install -y \
    openslide-tools \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir openslide-python pillow

# get pixman from build container
COPY --from=builder /usr/include/pixman-1/ /usr/include/pixman-1/

RUN mkdir data export

# clean this up later on...
COPY / .

ENTRYPOINT ["./docker/run.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]