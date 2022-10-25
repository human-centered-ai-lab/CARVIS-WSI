#FROM ubuntu:latest AS pixman-builder
FROM python:3.10-slim-bullseye AS pixman-builder

LABEL maintainer="stefan.baumann@medunigraz.at"

RUN apt-get update -y && apt-get upgrade -y \ 
    && apt-get install gcc cmake meson ninja-build wget -y

RUN wget https://www.cairographics.org/releases/pixman-0.40.0.tar.gz \
    && tar -xf pixman-0.40.0.tar.gz \
    && cd pixman-0.40.0/ \
    && mkdir build && cd build \
    && meson --prefix=/usr --buildtype=release \
    && ninja \
    && ninja test \
    && ninja install

FROM python:3.10.7-slim-bullseye

LABEL maintainer="stefan.baumann@medunigraz.at"
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && apt-get install -y \
    openslide-tools gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && python3 -m pip install --no-cache-dir openslide-python pillow pyvips

# get pixman from build container
COPY --from=pixman-builder /usr/include/pixman-1/ /usr/include/pixman-1/

RUN mkdir data export

COPY / .

ENTRYPOINT ["./docker/run.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]