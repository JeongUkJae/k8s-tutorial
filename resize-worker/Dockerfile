FROM python:3.6

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app/app.py /app/
CMD [ "python", "./app.py" ]
