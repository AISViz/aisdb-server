#FROM rust:alpine3.16
FROM rust:latest

# context is .. (see docker-compose.yml)
WORKDIR /usr/src/aisdb/receiver
COPY ./Cargo.toml ./build.rs /usr/src/aisdb/
COPY ./src /usr/src/aisdb/src
COPY ./aisdb/aisdb_sql /usr/src/aisdb/aisdb/aisdb_sql
COPY ./dispatcher /usr/src/aisdb/dispatcher
COPY receiver .

RUN cargo install --path .

#RUN touch -a ais_rx.db
#run chmod 777 ais_rx.db

CMD ["receiver"]