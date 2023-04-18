FROM python:3.9

RUN useradd --create-home appuser
USER appuser
RUN mkdir -p /home/appuser/metadata
WORKDIR /home/appuser/metadata
RUN chown appuser:appuser /home/appuser/metadata

#copy metadata app
COPY --chown=appuser:appuser . /home/appuser/metadata

#Install dependencies
RUN python -m venv /home/appuser/metadata/venv
ENV PATH="/home/appuser/metadata/venv/bin:$PATH"
RUN pip install wheel
RUN pip install .

EXPOSE 5002
CMD  ["gunicorn", "--config", "/home/appuser/metadata/gunicorn_config.py", "ensembl.production.metadata.app.main:app"]
