FROM python:3.12-bookworm

ARG MEDIA_ROOT

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/home/fastapi-blog
ENV WDIR=$APP_HOME/app

RUN mkdir $APP_HOME
RUN mkdir $WDIR

WORKDIR $WDIR

COPY requirements.txt $WDIR

RUN pip install --no-cache-dir -r $WDIR/requirements.txt
RUN apt-get update

COPY . $WDIR/

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000", "--reload"]
