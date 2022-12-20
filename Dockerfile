FROM python:3.8.8
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install aiogram
RUN pip3 install numpy
RUN pip3 install scipy
RUN chmod 755 .
COPY . .
