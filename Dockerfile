FROM python:latest

LABEL maintainer="stefan.baumann@medunigraz.at"
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && apt-get install -y \
    openslide-tools \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    ninja-build \
    meson \
    && rm -rf /var/lib/apt/lists/*

RUN ["python3", "-m", "pip", "install", "--no-cache-dir", "openslide-python", "pillow"]

# pixman
RUN wget https://www.cairographics.org/releases/pixman-0.40.0.tar.gz \
    && tar -xf pixman-0.40.0.tar.gz \
    && cd pixman-0.40.0/ \
    && mkdir build && cd build \
    && meson --prefix=/usr --buildtype=release \
    && ninja \
    && ninja test \
    && ninja install \
    && cd / \
    && rm -rf /pixman-0.40.0/ \
    && rm pixman-0.40.0.tar.gz \
    && pip3 cache purge \
    && apt-get purge -y meson ninja-build python3-pip python3-setuptools python3-wheel \
    && apt-get autoclean -y \
    && apt-get autoremove -y 

# multistage
# FROM alpine:latest
# where to find python build things?
#COPY --from=builder 

RUN ["mkdir", "data", "export"]

# clean this up later on...
COPY ["./src", "/src"]
COPY ["./arial.ttf", "/"]
COPY ["./docker/run.sh", "/"]

ENTRYPOINT ["./run.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]