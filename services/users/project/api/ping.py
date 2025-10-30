"""Ping blueprint for health checks."""
from flask import Blueprint, jsonify


ping_blueprint = Blueprint('ping', __name__)


@ping_blueprint.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint."""
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@ping_blueprint.route('/api/ping', methods=['GET'])
def api_ping():
    """API health check endpoint."""
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

