# Stage 1: Builder
# This stage compiles the Python application into a standalone executable using Nuitka.
FROM python:3.12 AS builder

RUN apt-get update && \
    apt-get install -y patchelf gcc ccache

# Install uv for package management
RUN pip install uv

# Set up the working directory and copy the project files
WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync
RUN uv venv --seed
RUN .venv/bin/python -m pip install -U Nuitka

COPY scripts/build.sh .
COPY . .
# Compile the application with Nuitka
# --standalone: Creates a folder with all the necessary files to run the application
# main.py: The entry point of the application
ARG CACHE_BUSTER=0
RUN --mount=type=cache,target=/root/.cache/nuitka \
    --mount=type=cache,target=/root/.ccache \
    bash scripts/build.sh

# Stage 2: Final Image
# This stage creates the final, minimal image for production.
FROM gcr.io/distroless/cc-debian12 AS runner

# Set the working directory
WORKDIR /app

# Copy the compiled application from the builder stage
COPY --from=builder /app/lazygopher .

# Set the command to run the application
CMD ["./lazygopher"]