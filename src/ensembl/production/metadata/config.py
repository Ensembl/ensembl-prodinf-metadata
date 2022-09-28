#!/usr/bin/env python
# .. See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
import os
from ensembl.production.core.config import load_config_yaml, parse_debug_var


class MetadataConfig:
    config_file_path = os.environ.get('METADATA_CONFIG_PATH')
    file_config = load_config_yaml(config_file_path)

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
