# Stage 1: Builder
# This stage compiles the Python application into a standalone executable using Nuitka.
FROM python:3.12 AS builder

RUN apt-get update && \
    apt-get install -y patchelf gcc 

# Install uv for package management
RUN pip install uv

# Set up the working directory and copy the project files
WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv, including Nuitka for compilation
RUN uv sync && uv venv --seed && .venv/bin/python -m pip install -U Nuitka

COPY . .
# Compile the application with Nuitka
# --standalone: Creates a folder with all the necessary files to run the application
# main.py: The entry point of the application
RUN .venv/bin/nuitka \
    --mode=onefile \
    --assume-yes-for-downloads \
    --lto=yes \
    --remove-output \
    --output-filename=lazygopher \
    --show-progress \
    --static-libpython=auto \
    --deployment \
    --prefer-source-code \
    --enable-plugins=anti-bloat \
    --noinclude-setuptools-mode=nofollow \
    --noinclude-pytest-mode=nofollow \
    --jobs=-1 \
    --clean-cache=ccache \
    --onefile-cache-mode=cached \
    main.py

# Stage 2: Final Image
# This stage creates the final, minimal image for production.
FROM gcr.io/distroless/cc-debian12 AS runner

# Set the working directory
WORKDIR /app

# Copy the compiled application from the builder stage
COPY --from=builder /app/lazygopher .

# Set the command to run the application
CMD ["./lazygopher"]