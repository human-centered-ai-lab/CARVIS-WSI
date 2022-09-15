FROM ubuntu:latest AS pixman-builder

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
ARG USER_ID
ARG GROUP_ID

RUN apt-get update && apt-get install -y \
    openslide-tools \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir openslide-python pillow

# get pixman from build container
COPY --from=pixman-builder /usr/include/pixman-1/ /usr/include/pixman-1/

RUN mkdir data export

COPY / .

# fix export file permissions
RUN addgroup --gid $GROUP_ID user \
    && adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user

USER user

ENTRYPOINT ["./docker/run.sh"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]