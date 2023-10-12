FROM ubuntu:18.04
WORKDIR /app
COPY . /app
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh
RUN conda --version
RUN conda update conda
COPY requirements.txt .
# Install requirements
RUN conda install pip
RUN conda install pandas=1.5.3
RUN conda install scipy=1.10.1
RUN pip install httpcore==0.9.1
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "Application/Application.py"]