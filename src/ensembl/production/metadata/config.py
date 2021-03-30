import os
from ensembl.production.core.config import load_config_yaml, parse_debug_var


config_file_path = os.environ.get('METADATA_CONFIG_PATH')
file_config = load_config_yaml(config_file_path)


class MetadataConfig:
    DEBUG = parse_debug_var(os.environ.get("DEBUG", file_config.get('debug', 'false')))
    HIVE_ANALYSIS = os.environ.get("HIVE_ANALYSIS",
                                   file_config.get('hive_analysis', 'metadata_updater_processdb'))
    HIVE_URI = os.environ.get("HIVE_URI", file_config.get('hive_uri', None))
    METADATA_URI = os.environ.get("METADATA_URI", file_config.get('metadata_uri', None))
    SWAGGER = {
      'title': 'Ensembl Production: Metadata Update API',
      'uiversion': 3,
      'hide_top_bar': True,
      'ui_params': {
        'defaultModelsExpandDepth': -1
      },
      'favicon': '/img/production.png',
      'specs_route': '/api'
    }
