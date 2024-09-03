# Builder stage
FROM ubuntu:20.04 AS builder

WORKDIR /app

# Set noninteractive installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
	apt-get install -y golang-go make pandoc python3 python3-pip && \
	rm -rf /var/lib/apt/lists/*

COPY server.go .
COPY Makefile .
COPY generate_css.py .
COPY . .

# Run make to update all .html files
RUN make

# Build the Go application with static linking
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o server server.go

# Final stage
FROM scratch

WORKDIR /app

# Copy the static executable
COPY --from=builder /app/server /app/server

# Copy files needed
COPY --from=builder /app/*.html /app/
COPY --from=builder /app/*.css /app/
COPY --from=builder /app/index.js /app/index.js
COPY --from=builder /app/blog/*.html /app/blog/
COPY --from=builder /app/APL386.ttf /app/APL386.ttf

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run the server when the container launches
CMD ["/app/server"]
