from __future__ import annotations

import orjson
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientResponseError
from loguru import logger

from bot.analytics.types import AbstractAnalyticsLogger, BaseEvent

GOOGLE_ANALYTICS_ENDPOINT = "https://www.google-analytics.com"


class GoogleAnalyticsTelegramLogger(AbstractAnalyticsLogger):
    def __init__(self, api_secret: str, measurement_id: str, base_url: str = GOOGLE_ANALYTICS_ENDPOINT) -> None:
        self._api_secret: str = api_secret
        self._measurement_id: str = measurement_id
        self._base_url: str = base_url
        self._headers = {"Content-Type": "application/json", "Accept": "*/*"}

    async def _send_request(
        self,
        event: BaseEvent,
    ) -> None:
        """Implementation of interaction with Amplitude API."""
        data = {"api_key": self._api_token, "events": [event.to_dict()]}

        async with ClientSession() as session:
            try:
                async with session.post(
                    self._base_url,
                    headers=self._headers,
                    data=orjson.dumps(data),
                    timeout=self._timeout,
                ) as response:
                    json_response = await response.json(content_type="application/json")
                    self._validate_response(json_response)
            except ClientConnectorError as e:
                logger.error(f"Failed to connect to Amplitude: {e}")
                return
            except ClientResponseError as e:
                logger.error(f"Failed to send request to Amplitude: {e}")
                return

        self._validate_response(json_response)

    @staticmethod
    def _validate_response(response: dict) -> dict:
        """Validate response."""
        if not response.get("ok"):
            name = response["error"]["name"]
            code = response["error"]["code"]

            logger.error(f"get error from cryptopay api | name: {name} | code: {code}")
            msg = f"Error in CryptoPay API call | name: {name} | code: {code}"
            raise ValueError(msg)

        logger.info(f"got response | ok: {response['ok']} | result: {response['result']}")
        return response

    async def log_event(
        self,
        event: BaseEvent,
    ) -> None:
        """Use this method to sends event to Google Analytics."""
        await self._send_request(event)
