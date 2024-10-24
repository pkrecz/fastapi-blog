FROM python:3.12-bookworm

WORKDIR /work-dir

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /work-dir/

RUN pip install --no-cache-dir -r /work-dir/requirements.txt

COPY . /work-dir/

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000", "--reload"]
