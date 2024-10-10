FROM ubuntu:18.04
RUN apt-get update
RUN apt-get -y install wget ssh curl openjdk-11-jdk python3-pip
RUN pip3 install pyspark

WORKDIR /opt/spark
RUN wget https://archive.apache.org/dist/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz
RUN tar -zxvf spark-3.5.1-bin-hadoop3.tgz
RUN rm spark-3.5.1-bin-hadoop3.tgz

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop/hadoop-3.3.6
ENV SPARK_HOME=/opt/spark/spark-3.5.1-bin-hadoop3
ENV PYSPARK_PYTHON=/usr/bin/python3
ENV PATH="$PATH:/opt/spark/spark-3.5.1-bin-hadoop3/sbin"
ENV SPARK_NO_DAEMONIZE=true
