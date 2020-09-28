#!/usr/bin/env python3

# CORTX MESSAGE-BUS-SERVER: errors.py
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


from cortx.utils.errors import BaseError
from cortx.utils.log import Log


MSG_BUS_INTERNAL_ERROR = 0x1001
MSG_BUS_INVALID_REQUEST = 0x1002


class MessageBusServerError(BaseError):
    """ Parent class for the Message bus error classes """

    _status_code = 0

    def __init__(self, rc=0, desc=None, message_id=None, message_args=None):
        super(MessageBusServerError, self).__init__(rc=rc, desc=desc, message_id=message_id,
                                                    message_args=message_args)
        Log.error(
            f"{self._rc}:{self._desc}:{self._message_id}:{self._message_args}")

    def get_status_code(self):
        return self._status_code


class InvalidRequest(MessageBusServerError):
    """
    This error will be raised when an invalid request is recevied.
    """

    _err = MSG_BUS_INVALID_REQUEST
    _desc = "Invalid request parameter"
    _status_code = 400

    def __init__(self, _desc=None, message_id=None, message_args=None):
        super(InvalidRequest, self).__init__(
            self._err, _desc, message_id, message_args)


class InternalError(MessageBusServerError):
    """
    This error will be raised when an internal error is occured.
    """

    _err = MSG_BUS_INTERNAL_ERROR
    _desc = "Internal Server error"
    _status_code = 500

    def __init__(self, _desc=None, message_id=None, message_args=None):
        super(InternalError, self).__init__(
            self._err, _desc, message_id, message_args)
