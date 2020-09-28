#!/usr/bin/env python3

# CORTX MESSAGE-BUS-SERVER: message_bus_worker.py
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


from cortx.utils.message_bus.message import MessageBusComm
from cortx.utils.message_bus.error import InvalidConfigError, ConnectionEstError, SendError, MsgFetchError
from cortx.utils.log import Log
from cortx.utils.schema.conf import Conf
from message_bus_server.common.errors import InternalError
from message_bus_server.common.const import BaseConstants


class ProducerWorker:
    """
    Sends messages to specified topic.
    """

    @staticmethod
    def send_message(request_param):
        try:
            client_id = request_param[BaseConstants.CLIENT_ID]
            topic = request_param[BaseConstants.TOPIC]
            messages = request_param[BaseConstants.MESSAGES]
            producer = MessageBusComm(
                client_id=client_id, comm_type=BaseConstants.COMM_TYPE_PRODUCER)
            producer.init()
            result = producer.send(messages, topic=topic)
            return result
        except ConnectionEstError as conn_est_err:
            raise InternalError(conn_est_err.error())
        except SendError as send_err:
            raise InternalError(send_err.error())
        except InvalidConfigError as invalid_config_err:
            raise InternalError(invalid_config_err.error())
        except Exception:
            raise InternalError("Could not send messages")


class ConsumerWorker:
    """
    Maintains a dictionary(key=group_id:consumer_name, value=consumer object) of consumers connections
    and receives messages from specified topic.
    """
    __consumers = dict()

    @staticmethod
    def receive_message(request_param):
        try:
            group_id = request_param[BaseConstants.GROUP_ID]
            consumer_name = request_param[BaseConstants.CONSUMER_NAME]
            topic = [request_param[BaseConstants.TOPIC]]
            consumer = ConsumerWorker.__consumers.get(
                ConsumerWorker.get_consumer_key(group_id, consumer_name))
            if consumer is None:
                consumer = MessageBusComm(
                    group_id=group_id, consumer_name=consumer_name, comm_type=BaseConstants.COMM_TYPE_CONSUMER)
                consumer.init()
                ConsumerWorker.__consumers[ConsumerWorker.get_consumer_key(
                    group_id, consumer_name)] = consumer

            result = consumer.recv(topic=topic)
            return result
        except ConnectionEstError as conn_est_err:
            raise InternalError(conn_est_err.error())
        except MsgFetchError as msg_fetch_err:
            raise InternalError(msg_fetch_err.error())
        except InvalidConfigError as invalid_config_err:
            raise InternalError(invalid_config_err.error())
        except Exception:
            raise InternalError("Could not fetch message")

    @staticmethod
    def message_receive_commit(request_param):
        try:
            group_id = request_param[BaseConstants.GROUP_ID]
            consumer_name = request_param[BaseConstants.CONSUMER_NAME]
            consumer = ConsumerWorker.__consumers.get(
                ConsumerWorker.get_consumer_key(group_id, consumer_name))
            if consumer is None:
                Log.warn(
                    f"No consumer found with consume_name: {consumer_name} and group_id: {group_id}")
                consumer = MessageBusComm(
                    group_id=group_id, consumer_name=consumer_name, comm_type=BaseConstants.COMM_TYPE_CONSUMER)
                consumer.init()
                ConsumerWorker.__consumers[ConsumerWorker.get_consumer_key(
                    group_id, consumer_name)] = consumer

            result = consumer.commit()
            return result
        except ConnectionEstError as conn_est_err:
            raise InternalError(conn_est_err.error())
        except InvalidConfigError as invalid_config_err:
            raise InternalError(invalid_config_err.error())
        except Exception:
            raise InternalError("Could not commit message received")

    @staticmethod
    def get_consumer_key(group_id, consumer_name):
        return f"{group_id}:{consumer_name}"
