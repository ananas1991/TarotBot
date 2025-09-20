# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for fonts and image processing
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY .env .
COPY Cards-jpg/ ./Cards-jpg/

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash tarot
RUN chown -R tarot:tarot /app
USER tarot

# Set default language (can be overridden)
ENV TAROT_LANGUAGE=en

# Expose port (optional, mainly for documentation)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import main; print('Bot is healthy')" || exit 1

# Default command - run in English mode
# Can be overridden with: docker run tarot-bot python main.py -l ru
CMD ["python", "main.py", "-l", "${TAROT_LANGUAGE:-en}"]