# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /api

COPY requirements_docker.txt requirements.txt
# COPY requirements_conda.txt requirements_conda.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio==0.8.1 -f https://download.pytorch.org/whl/torch_stable.html
# RUN ls
# RUN conda create --name cseproj --file requirements_conda.txt
# RUN conda activate cseproj

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]