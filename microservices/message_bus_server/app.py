#!/usr/bin/env python3

# CORTX MESSAGE-BUS-SERVER: app.py
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.


import sys
from flask import Flask, Blueprint, jsonify
from flask_restful import Api
from werkzeug.exceptions import HTTPException
from cortx.utils.log import Log
from cortx.utils.schema.payload import Yaml
from cortx.utils.schema.conf import Conf
from message_bus_server.common.const import BaseConstants, HttpStatusCodes, APIEndpoints
from message_bus_server.common.errors import MessageBusServerError
from message_bus_server.controllers.message_receive import ReceiveMessageResource
from message_bus_server.controllers.message_receive_commit import ReceiveCommitMessageResource
from message_bus_server.controllers.message_send import SendMessageResource


class MessageBusServerInit:
    """
    Initialize message bus server with config and logger. 
    """
    @staticmethod
    def init():
        Conf.init()
        Conf.load(BaseConstants.MSG_BUS_CONFIG_INDEX,
                  Yaml(BaseConstants.CONFIG_PATH))
        if BaseConstants.DEBUG_MODE in sys.argv:
            Conf.set(BaseConstants.MSG_BUS_CONFIG_INDEX,
                     "REST_SERVER.debug_mode", True)
            Conf.set(BaseConstants.MSG_BUS_CONFIG_INDEX,
                     "REST_SERVER.env", "development")
            Conf.save()
        Log.init("message_bus_service",
                 level=Conf.get(
                     BaseConstants.MSG_BUS_CONFIG_INDEX, "Log.log_level"),
                 log_path=Conf.get(BaseConstants.MSG_BUS_CONFIG_INDEX, "Log.log_path"))


class MessageBusServerApi(Api):
    """
    Overrides handle_error method to create custom error response.
    """

    def handle_error(self, err):
        err_response = {
            "error_code": None,
            "message_id": None,
            "message": None
        }

        status_code = HttpStatusCodes.INTERNAL_SERVER_ERROR

        if isinstance(err, MessageBusServerError):
            err_response["error_code"] = err.rc()
            err_response["message_id"] = err.message_id()
            err_response["message"] = err.error()
            message_args = err.message_args()
            status_code = err.get_status_code()
            if message_args is not None:
                err_response["error_format_args"] = err.message_args()
        elif isinstance(err, HTTPException):
            status_code = err.code
            err_response["message"] = getattr(err, "description", '')

        return jsonify(err_response), status_code


MessageBusServerInit.init()

message_bus_server_app = Flask(__name__)
api_bp = Blueprint("api", __name__)
api = MessageBusServerApi(api_bp)
message_bus_server_app.register_blueprint(api_bp)

# Add resources
api.add_resource(SendMessageResource, APIEndpoints.MESSAGE_SEND_V1)
api.add_resource(ReceiveMessageResource, APIEndpoints.MESSAGE_RECEIVE_V1)
api.add_resource(ReceiveCommitMessageResource,
                 APIEndpoints.MESSAGE_RECEIVE_COMMIT_V1)
