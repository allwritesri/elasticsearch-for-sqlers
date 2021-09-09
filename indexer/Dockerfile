FROM python:3.7

ADD app /indexer/app
ADD requirements.txt /indexer


RUN cd indexer && pip install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD [ "indexer/app/indexer.py" ]
