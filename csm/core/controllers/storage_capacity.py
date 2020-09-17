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

from .view import CsmView, CsmAuth
from eos.utils.log import Log
from csm.core.blogic import const
from csm.common.permission_names import Resource, Action
from csm.common.errors import InvalidRequest

from typing import Any, Callable, Dict


@CsmView._app_routes.view("/api/v1/capacity")
class StorageCapacityView(CsmView):
    """
    GET REST API view implementation for getting disk capacity details.
    """
    def __init__(self, request):
        super(StorageCapacityView, self).__init__(request)
        self._service = self.request.app[const.STORAGE_CAPACITY_SERVICE]

    @staticmethod
    def _create_convert_to_unit(unit: str, digits: int) -> Callable[[int], float]:
        """
        Creates an unit converter to one of the supported capacity units.

        See ``csm.const.blogic.const.CAPACITY_UNIT_LIST`` for details.

        :param unit: Result unit
        :param digits: Number of decimal digits of the result
        :return: Converter to intended unit, rounded according to the number of decimal digits
        """
        if unit not in const.CAPACITY_UNIT_LIST:
            raise ValueError(
                f'Invalid capacity unit. Valid units: {", ".join(const.CAPACITY_UNIT_LIST)}')
        if digits < 0:
            raise ValueError('Number of decimal digits must be non-negative')
        index = const.CAPACITY_UNIT_LIST.index(unit)
        divisor = 1000 ** index
        return lambda capacity: round(capacity / divisor, digits)

    @CsmAuth.permissions({Resource.STATS: {Action.LIST}})
    @Log.trace_method(Log.DEBUG)
    async def get(self) -> Dict[str, Any]:
        try:
            basic_unit = const.CAPACITY_UNIT_LIST[0].upper()
            unit = self.request.query.get('unit', basic_unit).upper()
            roundoff_digits = int(
                self.request.query.get('roundoff', const.DEFAULT_CAPACITY_DECIMAL_DIGITS))
            convert_to_unit = (
                (lambda x: x) if unit is basic_unit
                else StorageCapacityView._create_convert_to_unit(unit.upper(), roundoff_digits))
        except ValueError as e:
            raise InvalidRequest(e) from e
        capacity_details = await self._service.get_capacity_details()
        capacity_details[const.USAGE_PERCENTAGE] = round(
            capacity_details[const.USAGE_PERCENTAGE], roundoff_digits)
        for key in (const.SIZE, const.USED, const.AVAILABLE):
            capacity_details[key] = convert_to_unit(capacity_details[key])
        capacity_details[const.UNIT] = unit
        return capacity_details
