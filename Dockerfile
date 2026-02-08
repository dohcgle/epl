# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
# WeasyPrint needs: libpango-1.0-0, libpangoft2-1.0-0, libhazmat-dev, libprimitives-dev, libfreetype6-dev, liblcms2-dev, libopenjp2-7-dev
RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Install fonts (High Fidelity requirement)
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fontconfig \
    && fc-cache -f -v

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create media directory
RUN mkdir -p /app/media

# Add fonts
# Note: In a real scenario, you would copy TTF files here.
# For now, we will rely on system fonts or user to provide them.
# If files exist, COPY them.
# COPY fonts/ /usr/share/fonts/truetype/custom/
# RUN fc-cache -f -v

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
