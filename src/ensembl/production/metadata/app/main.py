import logging
import os
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
from flasgger import Swagger

from ensembl.production.metadata.config import MetadataConfig
from ensembl.production.core.models.hive import HiveInstance
from ensembl.production.core.exceptions import HTTPRequestError

app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(app_path, 'static')
template_path = os.path.join(app_path, 'templates')

app = Flask(__name__,
            static_url_path='',
            static_folder=static_path,
            template_folder=template_path,
            instance_relative_config=True)

app.config.from_object(MetadataConfig)

CORS(app)

Swagger(app, template_file='swagger.yml')

hive = None


def get_hive():
    global hive
    if hive is None:
        if app.config["HIVE_URI"] is None:
            raise RuntimeError('Undefined environment variable: HIVE_URI')
        else:
            hive = HiveInstance(app.config["HIVE_URI"])
    return hive


@app.route('/', methods=['GET'])
def info():
    return redirect('api')


@app.route('/jobs/', methods=['POST'])
def submit_job():
    if request.is_json:
        request.json["metadata_uri"] = app.config["METADATA_URI"]
        app.logger.debug('Submitting metadata job %s', request.json)
        try:
            analysis = app.config["HIVE_ANALYSIS"]
            job = get_hive().create_job(analysis, request.json)
        except ValueError as e:
            raise HTTPRequestError(str(e), 404)
        results = {"job_id": job.job_id}
        return jsonify(results), 201
    else:
        error_msg = 'Could not handle input of type %s', request.headers['Content-Type']
        app.logger.error(error_msg)
        raise HTTPRequestError(error_msg)


@app.route('/jobs/', methods=['GET'])
def jobs():
    app.logger.info('Retrieving jobs')
    analysis = app.config['HIVE_ANALYSIS']
    return jsonify(get_hive().get_all_results(analysis, child=True))


@app.route('/jobs/<int:job_id>', methods=['GET'])
def job_result(job_id):
    fmt = request.args.get('format')
    app.logger.debug('Format %s', fmt)
    if fmt == 'email':
        email = request.args.get('email')
        return job_email(email, job_id)
    elif fmt == 'failures':
        return failure(job_id)
    elif fmt is None:
        app.logger.info('Retrieving job with ID %s', job_id)
        try:
            result = get_hive().get_result_for_job_id(job_id, child=True)
        except ValueError as e:
            raise HTTPRequestError(str(e), 404)
        return jsonify(result)
    else:
        raise HTTPRequestError("Format " + fmt + " not valid")


def job_email(email, job_id):
    app.logger.info('Retrieving job with ID %s for %s', job_id, email)
    try:
        results = get_hive().get_result_for_job_id(job_id, child=True)
        if results['status'] == 'complete':
            results['subject'] = 'Metadata load for database %s is successful' % (results['output']['database_uri'])
            results['body'] = "Metadata load for database %s is successful\n" % (results['output']['database_uri'])
            results['body'] += "Load took %s" % (results['output']['runtime'])
        elif results['status'] == 'failed':
            job_failure = get_hive().get_job_failure_msg_by_id(job_id, child=True)
            results['subject'] = 'Metadata load for %s failed' % (results['input']['database_uri'])
            results['body'] = 'Metadata load failed with following message:\n'
            results['body'] += '%s' % job_failure.msg
    except ValueError as e:
        raise HTTPRequestError(str(e), 404)
    results['output'] = None
    return jsonify(results)


def failure(job_id):
    app.logger.info('Retrieving failure for job with ID %s', job_id)
    try:
        job_failure = get_hive().get_job_failure_msg_by_id(job_id, child=True)
    except ValueError as e:
        raise HTTPRequestError(str(e), 404)
    return jsonify({"msg": job_failure.msg})


@app.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        job = get_hive().get_job_by_id(job_id)
        get_hive().delete_job(job, child=True)
    except ValueError as e:
        raise HTTPRequestError(str(e), 404)
    return jsonify({"id": job_id})


@app.errorhandler(HTTPRequestError)
def handle_bad_request_error(e):
    app.logger.error(str(e))
    return jsonify(error=str(e)), e.status_code


if __name__ == "__main__":
    app.run(debug=True)
