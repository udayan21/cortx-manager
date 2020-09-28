#!/usr/bin/env python3

# CORTX MESSAGE-BUS-SERVER: const.py
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


class BaseConstants:
    BASE_PATH = "/opt/seagate/cortx/"

    #constants
    MSG_BUS_CONFIG_INDEX = "MESSAEGE_BUS_CONFIG"
    CLIENT_ID = "client_id"
    GROUP_ID = "group_id"
    CONSUMER_NAME = 'consumer_name'
    TOPIC = "topic"
    MESSAGES = "messages"
    DEBUG_MODE = "--debug"
    COMM_TYPE_PRODUCER = "PRODUCER"
    COMM_TYPE_CONSUMER = "CONSUMER"

    #services
    MSG_BUS_PRODUCER_SERVICE = "message_bus_producer_service"
    MSG_BUS_CONSUMER_SERVICE = "message_bus_consumer_service"

    #config
    CONFIG_PATH = f"{BASE_PATH}message_bus_server/conf/rest_server_config.yaml"


class HttpStatusCodes:
    # Successful - 2xx
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206

    # Client Error - 4xx
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405

    # Server Error - 5xx
    INTERNAL_SERVER_ERROR = 500


class APIEndpoints:
    API_VERSION_1 = "/api/v1"

    MESSAGE_SEND_V1 = f"{API_VERSION_1}/message/send"
    MESSAGE_RECEIVE_V1 = f"{API_VERSION_1}/message/receive"
    MESSAGE_RECEIVE_COMMIT_V1 = f"{API_VERSION_1}/message/receive_commit"