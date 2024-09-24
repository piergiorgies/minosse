FROM alpine:3.20.3

RUN apk add --no-cache python3 py3-pip
RUN apk add --no-cache build-base
RUN apk add --no-cache gcc
RUN apk add --no-cache openjdk11

RUN apk add --no-cache curl
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV $PATH="$PATH:$HOME/.cargo/bin"

ARG UNPRIVILEGED_USER=nonetwork

RUN adduser -D -H $UNPRIVILEGED_USER