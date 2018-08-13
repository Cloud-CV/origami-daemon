from flask import jsonify


def resp_demo_does_not_exist(demo_id):
    return jsonify({
        'response':
        'DemoDoesNotExist',
        'message':
        'Demo {} does not exist, try deploying first'.format(demo_id)
    }), 400


def resp_no_demo_instance_exist(demo_id):
    return jsonify({
        'response': 'NoDemoInstance',
        'message': 'No demo instance found for {}'.format(demo_id)
    }), 200


def resp_invalid_deploy_params():
    return jsonify({
        'response': 'InvalidRequestParameters',
        'message': 'Required parameters : bundle_path and demo_id'
    }), 400


def resp_invalid_demo_bundle(reason):
    return jsonify({
        'response': 'InvalidDemoBundle',
        'message': 'The demo bundle provided is not valid',
        'reason': '{}'.format(reason)
    }), 400


def resp_demo_deployment_trig(demo_dir):
    return jsonify({
        'response':
        'BundleValidated',
        'message':
        'Deploy has been triggred for bundle : {}, checks stats'.format(
            demo_dir)
    }), 200


def resp_docker_api_error(error):
    return jsonify({
        'response': 'InternalServerError',
        'message': 'Problem with docker API connection',
        'reason': '{}'.format(error)
    }), 500
