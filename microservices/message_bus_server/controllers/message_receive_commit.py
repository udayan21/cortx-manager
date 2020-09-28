#!/usr/bin/env python3

# CORTX MESSAGE-BUS-SERVER: message_receive_commit.py
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
from message_bus_server.services.message_bus_worker import ConsumerWorker
from message_bus_server.common.errors import InvalidRequest, InternalError


class ReceiveCommitRequestValidator(Schema):
    group_id = fields.String(required=True)
    consumer_name = fields.String(required=True)


class ReceiveCommitMessageResource(Resource):
    """
    REST resource to commit offset for the messages received for 
    consume with group_id and consumer_name.
    """

    def __init__(self):
        """
        Initialize request parser to parse request body.
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('group_id', type=str, location='json')
        self.reqparse.add_argument('consumer_name', type=str, location='json')
        super(ReceiveCommitMessageResource, self).__init__()

    def post(self):
        """
        Handle commit message received request.
        """
        req_args = self.reqparse.parse_args()
        try:
            request_param = ReceiveCommitRequestValidator().load(req_args,  unknown='EXCLUDE')
            result = ConsumerWorker.message_receive_commit(request_param)
            return {'message': result}, HttpStatusCodes.CREATED
        except ValidationError as ve:
            raise InvalidRequest(f"Invalid parameter: {ve}")
        except InternalError as internal_err:
            raise internal_err
