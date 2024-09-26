FROM ubuntu:24.04

RUN useradd -m nonetwork
RUN passwd -d nonetwork

RUN apt update
RUN apt install -y iptables
RUN apt install -y python3
RUN apt install -y python3-pip
RUN apt install -y python3-venv
RUN apt install -y build-essential
RUN apt install -y openjdk-17-jdk

RUN apt install -y curl
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV $PATH="$PATH:$HOME/.cargo/bin"

WORKDIR /app
COPY . .
RUN python3 -m venv venv
RUN /app/venv/bin/pip install -r requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Debugging purposes
# CMD ["sh", "-c", "while :; do sleep 1; done"]