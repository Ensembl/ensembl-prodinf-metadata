# Ensembl Metadata: Ensembl Production Service
The metadata service provides a set of endpoints to allow the
[ensembl_metadata](https://github.com/Ensembl/ensembl-metadata) database to be updated
with new data. These endpoints are used by the Ensembl Production handover service and the
[client that performs bulk updates](https://github.com/Ensembl/ensembl-prodinf-core/blob/main/src/ensembl/production/core/clients/metadata.py).

When the service is running, endpoint documentation is available at `/api`

## Installation
Clone the necessary repositories:

    git clone https://github.com/Ensembl/ensembl
    git clone https://github.com/Ensembl/ensembl-hive
    git clone https://github.com/Ensembl/ensembl-prodinf-core
    git clone https://github.com/Ensembl/ensembl-prodinf-metadata

Create a virtual environment and install Python requirements:

    mkvirtualenv prodinf -p /usr/bin/python3
    workon prodinf
    pip install -r ensembl-prodinf-core/requirements.txt
    pip install -r ensembl-prodinf-metadata/requirements.txt

## Hive configuration
The metadata service uses the
[MetadataUpdater_conf](https://github.com/Ensembl/ensembl-metadata/blob/master/modules/Bio/EnsEMBL/MetaData/Pipeline/MetadataUpdater_conf.pm)
hive pipeline to perform the necessary updates.

    SRV=h1-w # Or the MySQL command shortcut for another server
    init_pipeline.pl Bio::EnsEMBL::MetaData::Pipeline::MetadataUpdater_conf $($SRV details hive)

Start the beekeeper with the `--loop_until FOREVER` parameter.

## App configuration
The app requires the MySQL uri of the metadata database, and the uri of the pipeline database.

    export HIVE_URI='mysql://user:password@host:port/hive_db'
    export METADATA_URI='mysql://user:password@host:port/metadata_db'

Alternatively, a yaml file can be used to provide the uris:

    export METADATA_CONFIG_PATH=<path>/metadata_config.yaml

## Start a local Flask application

    BASE_DIR=$(pwd) # Or wherever the repositories were installed
    export PYTHONPATH=${BASE_DIR}/ensembl-prodinf-metadata/src:${BASE_DIR}/ensembl-prodinf-core/src
    export FLASK_APP=ensembl.production.metadata.app.main
    export FLASK_ENV=development
    flask run
