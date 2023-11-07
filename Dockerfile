FROM python:3.9

RUN pip install --upgrade pip

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENV PORT 8080
EXPOSE 8080

CMD streamlit run Main.py --server.port 8080