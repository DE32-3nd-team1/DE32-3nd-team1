# Dockerfile
FROM spark:python3

# Switch to root user
USER root

COPY amount.py amount.py
# Install pymysql and vim
RUN apt-get update && \
    apt-get install -y python3-pip vim && \
    pip3 install pymysql && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Optional: Switch back to a non-root user if needed
# USER spark

