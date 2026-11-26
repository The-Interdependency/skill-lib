# ratios: loc_comments=153:1 imports_exports=13:2 calls_definitions=98:9
"""Exercise the installed skill-lib service across real MCP transports."""

import asyncio
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import socket
import subprocess
import sysconfig
import tempfile
import unittest
from unittest.mock import patch

try:
    SDK_MAJOR = int(version("mcp").split(".", 1)[0])
except PackageNotFoundError:
    SDK_MAJOR = 0

REQUIRE_INSTALLED = os.environ.get("SKILL_LIB_REQUIRE_MCP") == "1"
if SDK_MAJOR == 2:
    from mcp import Client, MCPError, StdioServerParameters

SOURCE = Path(__file__).resolve().parents[1]
COMMAND = Path(sysconfig.get_path("scripts")) / ("skill-lib-mcp.exe" if os.name == "nt" else "skill-lib-mcp")
TOOLS = {"list_skills", "read_skill", "activate_skills", "list_skill_files", "read_skill_file"}


def payload(result):
    if result.is_error:
        raise AssertionError(result.content)
    if result.structured_content is not None or len(result.content) != 1:
        raise AssertionError("expected one JSON text block without a structured copy")
    return json.loads(result.content[0].text)


@unittest.skipUnless(REQUIRE_INSTALLED or (SDK_MAJOR == 2 and COMMAND.is_file()),
                     "install the skill-lib MCP server to run its transport tests")
class McpServerTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        if SDK_MAJOR != 2 or not COMMAND.is_file():
            raise RuntimeError("install the skill-lib wheel and its MCP v2 dependency in the test interpreter")

    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.cwd = Path(workspace.name)
        (self.cwd / "skills.json").write_text('{"skills":[]}', encoding="utf-8")

    def client(self, *args, mode="auto"):
        params = StdioServerParameters(command=str(COMMAND), args=list(args), cwd=str(self.cwd))
        return Client(params, mode=mode)

    async def test_discovery_search_and_exact_resources(self):
        expected = {entry["name"] for entry in json.loads((SOURCE / "skills.json").read_bytes())["skills"]}
        async with self.client() as client:
            self.assertTrue(client.protocol_version)
            self.assertEqual({tool.name for tool in (await client.list_tools()).tools}, TOOLS)
            templates = (await client.list_resource_templates()).resource_templates
            declared = {item.uri_template for item in templates}
            self.assertIn("skill-lib://catalog/skills/{name}", declared)
            self.assertIn("skill-lib://support/{name}/{sha256}", declared)
            resources = (await client.list_resources()).resources
            self.assertIn("skill-lib://catalog/index", {str(item.uri) for item in resources})
            index = json.loads((await client.read_resource("skill-lib://catalog/index")).contents[0].text)
            self.assertEqual({row["name"] for row in index["skills"]}, expected)
            self.assertTrue(all("instructions" not in row for row in index["skills"]))
            match = payload(await client.call_tool("list_skills", {"query": "typed-meta-frontend"}))
            self.assertIn("typed-meta-frontend", {row["name"] for row in match["skills"]})
            name = "distributed-publication"
            source = (SOURCE / name / "SKILL.md").read_bytes()
            text = source.decode("utf-8")
            uri = f"skill-lib://catalog/skills/{name}"
            self.assertEqual((await client.read_resource(uri)).contents[0].text, text)
            result = await client.call_tool("read_skill", {"name": name})
            item = payload(result)
            self.assertEqual(item["sha256"], sha256(source).hexdigest())
            self.assertEqual(item["instructions"], text)

    async def test_full_retained_changed_and_reset(self):
        roots = ["typed-meta-frontend", "distributed-publication"]
        async with self.client() as client:
            async def activate(retained=None):
                args = {"roots": roots}
                if retained is not None:
                    args["retained"] = retained
                return await client.call_tool("activate_skills", args)

            first = await activate()
            items = payload(first)["skills"]
            names = [row["name"] for row in items]
            by_name = {row["name"]: row for row in items}
            self.assertEqual(len(names), 6)
            self.assertEqual(set(names), {*roots, "interdependent-work-graph", "doc-build", "msdmd", "meta-module-build"})
            self.assertLess(names.index("msdmd"), names.index("typed-meta-frontend"))
            self.assertEqual(by_name["interdependent-work-graph"]["reasons"],
                             [{"kind": "load_with", "source": "distributed-publication"}])
            self.assertEqual({r["source"] for r in by_name["msdmd"]["reasons"]},
                             {"doc-build", "meta-module-build", "typed-meta-frontend"})
            for row in items:
                source = (SOURCE / row["name"] / "SKILL.md").read_bytes()
                self.assertEqual(row["instructions"], source.decode("utf-8"))
                self.assertEqual(row["sha256"], sha256(source).hexdigest())
            revisions = {row["name"]: row["sha256"] for row in items}
            hit = await activate(revisions)
            kept = payload(hit)["skills"]
            self.assertTrue(all(row["instructions_retained"] and "instructions" not in row for row in kept))
            partial = payload(await activate({**revisions, "doc-build": "0" * 64}))["skills"]
            self.assertEqual([r["name"] for r in partial if "instructions" in r], ["doc-build"])
            self.assertEqual(payload(await activate({}))["skills"], items)

    async def test_files_and_hidden_dependency_over_legacy_stdio(self):
        async with self.client("--allow-skill", "msdmd", "--allow-skill", "distributed-publication",
                               mode="legacy") as client:
            listed = payload(await client.call_tool("list_skills", {}))["skills"]
            self.assertEqual({r["name"] for r in listed}, {"distributed-publication", "msdmd"})
            blocked = await client.call_tool("activate_skills", {"roots": ["distributed-publication"]})
            self.assertTrue(blocked.is_error)
            self.assertNotIn("interdependent-work-graph", str(blocked.content))
            self.assertTrue((await client.call_tool("read_skill", {"name": "doc-build"})).is_error)
            with self.assertRaises(MCPError):
                await client.read_resource("skill-lib://catalog/skills/doc-build")
            path = "references/metadata-conventions.md"
            rows = payload(await client.call_tool("list_skill_files", {"name": "msdmd"}))["files"]
            entry = next(row for row in rows if row["path"] == path)
            original = (SOURCE / "msdmd" / path).read_bytes()
            self.assertEqual(entry["sha256"], sha256(original).hexdigest())
            support = await client.call_tool("read_skill_file", {"name": "msdmd", "path": path})
            self.assertEqual(payload(support)["text"], original.decode("utf-8"))
            read = await client.read_resource(entry["uri"])
            self.assertEqual(read.contents[0].text, original.decode("utf-8"))
            refused = await client.call_tool("read_skill_file", {"name": "msdmd", "path": "unknown.md"})
            self.assertTrue(refused.is_error)
            with self.assertRaises(MCPError):
                await client.read_resource("skill-lib://support/msdmd/" + "0" * 64)

    async def test_streamable_http_loopback(self):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        process = subprocess.Popen([str(COMMAND), "--transport", "streamable-http", "--port", str(port),
                                    "--allow-skill", "msdmd"], cwd=self.cwd,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        try:
            async def ready():
                while process.poll() is None:
                    try:
                        _, writer = await asyncio.open_connection("127.0.0.1", port)
                    except OSError:
                        await asyncio.sleep(0.05)
                        continue
                    writer.close()
                    await writer.wait_closed()
                    return
                raise RuntimeError(f"HTTP MCP server exited with {process.returncode}")
            await asyncio.wait_for(ready(), timeout=20)
            with patch.dict(os.environ, {"NO_PROXY": "*", "no_proxy": "*"}):
                async with Client(f"http://127.0.0.1:{port}/mcp") as client:
                    rows = payload(await client.call_tool("list_skills", {}))["skills"]
                    self.assertEqual([r["name"] for r in rows], ["msdmd"])
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
# ratios: loc_comments=153:1 imports_exports=13:2 calls_definitions=98:9
