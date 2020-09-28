#!/usr/bin/env python3

# CORTX MESSAGE-BUS-SERVER: message_send.py
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


from flask_restful import Resource, reqparse
from marshmallow import Schema, fields, ValidationError
from message_bus_server.common.const import HttpStatusCodes
from message_bus_server.services.message_bus_worker import ProducerWorker
from message_bus_server.common.errors import InvalidRequest, InternalError


class SendRequestValidator(Schema):
    topic = fields.String(required=True)
    messages = fields.List(fields.String(), required=True)
    client_id = fields.String(required=True)


class SendMessageResource(Resource):
    """
    REST resource to send messages received on topic for
    producer with client_id.
    """

    def __init__(self):
        """
        Initialize request parser to parse request body.
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('topic', type=str, location='json')
        self.reqparse.add_argument('messages', type=list, location='json')
        self.reqparse.add_argument('client_id', type=str, location='json')
        super(SendMessageResource, self).__init__()

    def post(self):
        """
        Handle send message request.
        """
        req_args = self.reqparse.parse_args()
        try:
            request_param = SendRequestValidator().load(req_args,  unknown='EXCLUDE')
            ProducerWorker.send_message(request_param)
            return {"message": "Messages sent successfully"}, HttpStatusCodes.CREATED
        except ValidationError as ve:
            raise InvalidRequest(f"Invalid parameter: {ve}")
        except InternalError as internal_err:
            raise internal_err
