# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for GeoDjango (GDAL, GEOS, PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libspatialindex-dev \
    gettext \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Find and verify library locations (auto-detect architecture)
# Create wrapper script that detects library paths at runtime
RUN \
    echo "=== Detecting architecture ===" && \
    ARCH=$(dpkg-architecture -q DEB_HOST_MULTIARCH 2>/dev/null || uname -m | sed 's/x86_64/x86_64-linux-gnu/; s/aarch64/aarch64-linux-gnu/') && \
    LIB_DIR="/usr/lib/$ARCH" && \
    echo "Architecture: $ARCH" && \
    echo "Library directory: $LIB_DIR" && \
    echo "=== Checking installed GDAL/GEOS libraries ===" && \
    find /usr/lib -name "*libgdal*" 2>/dev/null | head -5 && \
    find /usr/lib -name "*libgeos_c*" 2>/dev/null | head -5 && \
    echo "=== Library files in $LIB_DIR ===" && \
    ls -la "$LIB_DIR"/libgdal* "$LIB_DIR"/libgeos* 2>/dev/null || echo "Checking alternate locations..." && \
    # Find actual library files and create symlinks if needed
    GDAL_REAL=$(find "$LIB_DIR" -name "libgdal.so.*" -type f | sort -V | tail -1) && \
    GEOS_REAL=$(find "$LIB_DIR" -name "libgeos_c.so.*" -type f | sort -V | tail -1) && \
    if [ -z "$GDAL_REAL" ]; then \
        GDAL_REAL=$(find /usr/lib -name "libgdal.so.*" -type f | sort -V | tail -1); \
    fi && \
    if [ -z "$GEOS_REAL" ]; then \
        GEOS_REAL=$(find /usr/lib -name "libgeos_c.so.*" -type f | sort -V | tail -1); \
    fi && \
    echo "GDAL library found: $GDAL_REAL" && \
    echo "GEOS library found: $GEOS_REAL" && \
    # Create symlinks if needed
    if [ -n "$GDAL_REAL" ] && [ ! -e "$LIB_DIR/libgdal.so" ]; then \
        cd "$LIB_DIR" && ln -sf $(basename "$GDAL_REAL") libgdal.so && echo "Created GDAL symlink at $LIB_DIR/libgdal.so"; \
    fi && \
    if [ -n "$GEOS_REAL" ] && [ ! -e "$LIB_DIR/libgeos_c.so.1" ]; then \
        cd "$LIB_DIR" && ln -sf $(basename "$GEOS_REAL") libgeos_c.so.1 && echo "Created GEOS symlink at $LIB_DIR/libgeos_c.so.1"; \
    fi && \
    # Verify symlinks exist
    echo "=== Final check ===" && \
    if [ -e "$LIB_DIR/libgdal.so" ]; then \
        echo "✓ GDAL symlink exists: $LIB_DIR/libgdal.so"; \
    else \
        echo "✗ GDAL symlink NOT found, will use: $GDAL_REAL"; \
    fi && \
    if [ -e "$LIB_DIR/libgeos_c.so.1" ]; then \
        echo "✓ GEOS symlink exists: $LIB_DIR/libgeos_c.so.1"; \
    else \
        echo "✗ GEOS symlink NOT found, will use: $GEOS_REAL"; \
    fi && \
    ls -la "$LIB_DIR"/libgdal* "$LIB_DIR"/libgeos* 2>/dev/null || true

# Set environment variables - try common locations first
# Django will auto-detect if these don't exist, or we can override via settings
ARG BUILDARCH
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so.1

# Copy requirements first for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --no-input

# Expose port (Render uses $PORT environment variable)
EXPOSE 8000

# Run migrations and start server
# Use PORT environment variable (Render sets this automatically)
CMD python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-8000} core.asgi:application

