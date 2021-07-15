"""Define /device endpoints."""
from typing import Awaitable, Callable

from .const import GET_DEVICE_PAYLOAD, GET_PAYLOAD_HEADERS, COMMAND_URL, COMMAND_HEADERS


class Device:  # pylint: disable=too-few-public-methods
    """Define an object to handle the endpoints."""

    def __init__(self, request: Callable[..., Awaitable], id_token: str) -> None:
        """Initialize."""
        self._request: Callable[..., Awaitable] = request
        self._id_token: str = id_token
        self.headers = {
            'User-Agent': 'okhttp/3.12.1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f"Bearer {self._id_token}",
            'Accept-Encoding': 'gzip',
            'Accept': 'application/json, text/plain, */*'
        }

    async def get_info(self, device_id: str) -> dict:
        """Return device specific data.
        :param device_id: Unique identifier for the device
        :type device_id: ``str``
        :rtype: ``dict``
        """
        payload = GET_DEVICE_PAYLOAD % (device_id)

        return await self._request("post", "https://s34ox7kri5dsvdr43bfgp6qh6i.appsync-api.us-east-1.amazonaws.com/graphql",data=payload,headers=GET_PAYLOAD_HEADERS)

    async def patch_recirculation(self, thing_name: str, duration: int) -> None:
        """Use the patch URL to make our requests"""
        data = '{"recirculation_duration": "%s","set_recirculation_enabled":true}' % duration

        return await self._request("patch", f"https://698suy4zs3.execute-api.us-east-1.amazonaws.com/Prod/thing/{thing_name}/shadow", headers=self.headers, data=data)

    async def patch_stop_recirculation(self, thing_name: str) -> None:
        """Use the patch URL to make our requests"""
        data = '{"set_recirculation_enabled":false}'

        return await self._request("patch", f"https://698suy4zs3.execute-api.us-east-1.amazonaws.com/Prod/thing/{thing_name}/shadow", headers=self.headers, data=data)

    async def patch_set_temperature(self, thing_name: str, temperature: int) -> None:
        """Use the patch URL to make our requests"""
        if temperature % 5 == 0:
            data = '{"set_domestic_temperature":%s}' % temperature

            return await self._request("patch", f"https://698suy4zs3.execute-api.us-east-1.amazonaws.com/Prod/thing/{thing_name}/shadow", headers=self.headers, data=data)


    async def start_recirculation(self, user_uuid: str, device_id: str, duration: int, additional_params={}) -> None:
        """start recirculation on the specified device"""

        payload = "user=%s&thing=%s&attribute=set_priority_status&value=true" % (user_uuid, device_id)

        await self._request(
            "post",
            COMMAND_URL,
            data=payload,
            headers=COMMAND_HEADERS
        )

        payload = "user=%s&thing=%s&attribute=recirculation_duration&value=%s" % (user_uuid, device_id, duration)
        await self._request(
            "post",
            COMMAND_URL,
            data=payload,
            headers=COMMAND_HEADERS
        )

        payload = "user=%s&thing=%s&attribute=set_recirculation_enabled&value=true" % (user_uuid, device_id)
        await self._request(
            "post",
            COMMAND_URL,
            data=payload,
            headers=COMMAND_HEADERS
        )

        return True

    async def stop_recirculation(self, user_uuid: str, device_id: str) -> None:
        payload = "user=%s&thing=%s&attribute=set_recirculation_enabled&value=false" % (user_uuid, device_id)

        await self._request(
            "post",
            COMMAND_URL,
            data=payload,
            headers=COMMAND_HEADERS
        )

        return True

    async def set_temperature(self, user_uuid: str, device_id: str, temperature: int) -> None:
        """set the temperature of the hot water heater"""

        #check if the temperature is a multiple of 5. Rinnai only takes temperatures this way
        if temperature % 5 == 0:
            payload="user=%s&thing=%s&attribute=set_domestic_temperature&value=%s" % (user_uuid, device_id, temperature)

            await self._request(
                "post",
                COMMAND_URL,
                data=payload,
                headers=COMMAND_HEADERS
            )

        return True