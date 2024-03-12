# Use a base Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /feed

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN pip install -e git+https://github.com/delphos-quant/dxlib.git@main#egg=dxlib