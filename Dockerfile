FROM continuumio/miniconda

WORKDIR /usr/src/ellie

COPY src ./
RUN pip install -r requirements.txt
EXPOSE 8080

CMD ["python", "app.py"]