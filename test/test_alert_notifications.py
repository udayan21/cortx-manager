# CORTX-CSM: CORTX Management web and CLI interface.
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

import asyncio
import copy
import unittest
from email.message import EmailMessage
from importlib import import_module

from csm.common.conf import Conf
from csm.common.email import SmtpServerConfiguration
from csm.common.observer import Observable
from csm.common.template import Template
from csm.core.blogic import const
from csm.core.blogic.models.alerts import IAlertStorage
from csm.core.data.models.system_config import EmailConfig, Notification, SystemConfigSettings
from csm.core.services.alerts import AlertEmailNotifier, AlertHttpNotifyService, AlertMonitorService


class MockAlertRepository(IAlertStorage):
    async def store(self, alert):
        pass

    async def retrieve(self, alert_id):
        return None

    async def retrieve_by_hw(self, hw_id):
        return None

    async def update(self, alert):
        return None

    async def update_by_hw_id(self, hw_id, update_params):
        pass

    async def retrieve_by_range(self, *args, **kwargs):
        return []

    async def retrieve_by_sensor_info(self, sensor_info, module_type):
        return []

    async def count_by_range(self, *args, **kwargs):
        return 0

    async def retrieve_all(self) -> list:
        return []


class MockAlertPlugin:
    def __init__(self, alert):
        self.monitor_callback = None
        self.alert = alert
        self.health_plugin = None

    def init(self, callback_fn, health_plugin):
        self.monitor_callback = callback_fn
        self.health_plugin = health_plugin

    def process_request(self, cmd):
        if cmd == 'listen':
            self.monitor_callback(self.alert)


class MockEmailQueue(Observable):
    async def enqueue_email(self, message, config):
        self._notify_listeners(message, config, loop=asyncio.get_event_loop())

    async def enqueue_bulk_email(self, message: EmailMessage, recipients,
                                 config: SmtpServerConfiguration):
        msg = copy.deepcopy(message)
        msg['To'] = recipients[0]
        await self.enqueue_email(msg, config)


class MockSystemConfigManager:
    def __init__(self, value):
        self.value = value

    async def get_current_config(self):
        return self.value


t = unittest.TestCase()

RAW_ALERT = {
    "alert_uuid": "abcd",
    "sensor_info": "hw01234",
    "state": "missing",
    "created_time": 0,
    "updated_time": 0,
    "resolved": False,
    "acknowledged": False,
    "severity": "no"
}

ALERT_MODEL = None

email_config = EmailConfig()
email_config.smtp_server = "localhost"
email_config.smtp_port = 1234
email_config.smtp_protocol = "tls"
email_config.smtp_sender_email = "from@email.com"
email_config.smtp_sender_password = "1234"
email_config.email = "to@email.com"
email_config.weekly_email = False


async def test_alert_monitor_service():
    """Tests if AlertMonitorService notifies its observers about new alerts"""
    mock_repo = MockAlertRepository()
    mock_plugin = MockAlertPlugin(RAW_ALERT)

    been_called = False

    def handle_alert_cb(alert):
        nonlocal been_called
        global ALERT_MODEL  # pylint: disable=global-statement
        t.assertIsNotNone(alert)

        been_called = True
        ALERT_MODEL = alert

    product = Conf.get(const.CSM_GLOBAL_INDEX, "PRODUCT.name") or 'eos'
    health_plugin = import_module(f'csm.plugins.{product}.{const.HEALTH_PLUGIN}')
    http_notifications = AlertHttpNotifyService()
    monitor_service = AlertMonitorService(mock_repo, mock_plugin, health_plugin.HealthPlugin(),
                                          http_notifications)
    monitor_service.add_listener(handle_alert_cb)
    monitor_service.start()
    await asyncio.sleep(1)  # We need to release event loop for some time

    monitor_service.stop()
    t.assertTrue(been_called, "AlertMonitorService did not notify its observers")


async def test_email_notification():
    t.assertIsNotNone(ALERT_MODEL, 'test_alert_monitor_service must run successfully before this')

    notif = Notification()
    notif.email = email_config

    system_config = SystemConfigSettings()
    system_config.notifications = notif

    def email_enqueued(message, config):
        t.assertEqual(email_config.smtp_server, config.smtp_host)
        t.assertEqual(email_config.smtp_port, config.smtp_port)
        t.assertEqual(email_config.smtp_sender_email, config.smtp_login)
        t.assertEqual(email_config.smtp_sender_password, config.smtp_password)
        t.assertEqual(True, config.smtp_use_ssl)

        t.assertEqual(message['To'], email_config.email)
        t.assertEqual(message['From'], email_config.smtp_sender_email)

    mock_queue = MockEmailQueue()
    mock_queue.add_listener(email_enqueued)
    mock_config_mgr = MockSystemConfigManager(system_config)
    template = Template('Email template')
    email_notificator = AlertEmailNotifier(mock_queue, mock_config_mgr, template)
    await email_notificator.handle_alert(ALERT_MODEL)


def run_tests():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_alert_monitor_service())
    loop.run_until_complete(test_email_notification())


test_list = [run_tests]
