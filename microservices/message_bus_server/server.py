#!/usr/bin/env python3

# CORTX MESSAGE-BUS-SERVER: server.py
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


from cortx.utils.schema.conf import Conf
from message_bus_server.app import message_bus_server_app
from message_bus_server.common.const import BaseConstants


if __name__ == "__main__":
    message_bus_server_app.run(host=Conf.get(BaseConstants.MSG_BUS_CONFIG_INDEX, "REST_SERVER.hostname"),
                               port=Conf.get(
                                   BaseConstants.MSG_BUS_CONFIG_INDEX, "REST_SERVER.port"),
                               debug=Conf.get(
                                   BaseConstants.MSG_BUS_CONFIG_INDEX, "REST_SERVER.debug_mode"),
                               load_dotenv=Conf.get(BaseConstants.MSG_BUS_CONFIG_INDEX, "REST_SERVER.env"))
