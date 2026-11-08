import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import AsyncMock, Mock

from speedport import Speedport
from speedport.__main__ import check_args
from speedport.api import SpeedportApi
from speedport.connection import Connection, decode, encode


class CompatibilityTests(unittest.TestCase):
    def test_cli_starts_without_router_or_credentials(self):
        for args in (("--help",), ("ip-info", "--help")):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, "-m", "speedport", *args],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("ip-info", result.stdout)

    def test_encrypted_router_response(self):
        response = [
            {"varid": "public_ip_v4", "varvalue": "192.0.2.1"},
            {"varid": "public_ip_v6", "varvalue": "2001:db8::1"},
        ]
        self.assertEqual(
            decode(encode(json.dumps(response))),
            {"public_ip_v4": "192.0.2.1", "public_ip_v6": "2001:db8::1"},
        )


class AsyncCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_session_lifecycle(self):
        connection = Connection("http://192.0.2.1")
        async with connection as opened:
            self.assertIs(opened, connection)
            self.assertFalse(connection._session.closed)
        self.assertTrue(connection._session.closed)

    async def test_ip_query_authenticates_and_refreshes(self):
        api = SpeedportApi(password="test-password")
        api._api = Mock(
            is_logged_in=False,
            login=AsyncMock(),
            get=AsyncMock(
                return_value={
                    "public_ip_v4": "192.0.2.1",
                    "public_ip_v6": "2001:db8::1",
                }
            ),
        )
        router = Speedport()
        router._api = api
        info = await router.ip_info
        self.assertEqual(info["public_ip_v4"], "192.0.2.1")
        self.assertEqual(router.public_ip_v6, "2001:db8::1")
        api.api.login.assert_awaited_once_with("test-password")
        api.api.get.assert_awaited_once_with(
            "data/IPData.json",
            referer="html/content/internet/con_ipdata.html",
            auth=True,
        )

    async def test_ipv4_command_prints_only_the_address(self):
        router = Speedport()
        router._api = Mock(
            get_ip_data=AsyncMock(
                return_value={
                    "public_ip_v4": "192.0.2.1",
                    "public_ip_v6": "2001:db8::1",
                }
            )
        )
        output = io.StringIO()
        with redirect_stdout(output):
            await check_args(router, {"ip_info": True, "ipv4": True})
        self.assertEqual(output.getvalue(), "192.0.2.1\n")
