FROM python:3.6
WORKDIR /views
ADD . /views
COPY requirements.txt /views
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install ibm_db
EXPOSE 8080
CMD ["python","app.py"]