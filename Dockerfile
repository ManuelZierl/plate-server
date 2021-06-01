FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python test_app.py
RUN python setup_db.py
ENTRYPOINT ["python"]
CMD ["app.py"]