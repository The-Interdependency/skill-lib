# ratios: loc_comments=76:15 imports_exports=10:2 calls_definitions=37:12
"""Serve the skill library over MCP. Run skill-lib-mcp or python -m skill_lib.mcp_server."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp.types import ToolAnnotations

from .mcp_assets import SkillAssets
from .mcp_catalog import CatalogError, SkillCatalog
from .mcp_data import catalog_root


def _json_text(payload: dict) -> str:
    """Encode one text block for clients that forward MCP results to a model."""
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _catalog_call(function, *args, error=ToolError):
    """Report anticipated catalog failures using the MCP tool or resource error channel."""
    try:
        return function(*args)
    except CatalogError as exc:
        raise error(str(exc)) from exc


def create_server(root: Path, *, allowed: list[str] | None = None) -> MCPServer:
    """Load one library snapshot and expose its admitted skills and supporting text."""
    catalog = SkillCatalog(root, allowed=allowed)
    assets = SkillAssets(root, catalog)
    server = MCPServer(
        "skill-lib",
        instructions=(
            "Search list_skills to find relevant skills. Use activate_skills to obtain "
            "the instructions and dependency reasons for a task. An empty retained map "
            "requests all instructions. Supporting text is available through list_skill_files."
        ),
        subscriptions=False,
    )
    readonly = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)

    @server.tool(annotations=readonly, structured_output=False)
    def list_skills(query: str = "") -> str:
        """List visible skill names, descriptions and instruction hashes. Filter by substring."""
        needle = query.strip().casefold()
        skills = [row for row in catalog.discover()
                  if needle in row["name"].casefold() or needle in row["description"].casefold()]
        return _json_text({"catalog_sha256": catalog.catalog_sha256, "skills": skills})

    @server.tool(annotations=readonly, structured_output=False)
    def read_skill(name: str) -> str:
        """Read one visible skill's exact Markdown instructions and their SHA-256 revision."""
        return _json_text(_catalog_call(catalog.read, name))

    @server.tool(annotations=readonly, structured_output=False)
    def activate_skills(roots: list[str], retained: dict[str, str] | None = None) -> str:
        """Resolve task skills, their prerequisites and co-loads. Return ordered skills and reasons.

        A client may supply retained name-to-SHA-256 pairs confirmed in the current model
        context on this call. Omit retained to receive every required instruction body.
        """
        return _json_text(_catalog_call(catalog.activate, roots, retained))

    @server.tool(annotations=readonly, structured_output=False)
    def list_skill_files(name: str) -> str:
        """List a visible skill's admitted supporting files, relative paths and resource URIs."""
        return _json_text({"files": _catalog_call(assets.list_files, name)})

    @server.tool(annotations=readonly, structured_output=False)
    def read_skill_file(name: str, path: str) -> str:
        """Read the exact supporting text at a path returned by list_skill_files."""
        return _json_text(_catalog_call(assets.read_file, name, path))

    @server.resource("skill-lib://catalog/index", mime_type="application/json")
    def skill_index() -> str:
        """Discover visible skills and their instruction revisions."""
        return list_skills()

    @server.resource("skill-lib://catalog/skills/{name}", mime_type="text/markdown")
    def skill_instructions(name: str) -> str:
        """Read the canonical Markdown instructions of a visible skill."""
        return _catalog_call(catalog.read, name, error=ResourceNotFoundError)["instructions"]

    @server.resource("skill-lib://support/{name}/{sha256}", mime_type="text/plain")
    def skill_support(name: str, sha256: str) -> str:
        """Read a supporting text resource listed for this skill and revision."""
        return _catalog_call(assets.read_digest, name, sha256, error=ResourceNotFoundError)

    return server


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transport", choices=("stdio", "streamable-http"), default="stdio")
    parser.add_argument("--port", type=int, default=8000, help="loopback HTTP port (default 8000)")
    parser.add_argument("--catalog-root", type=Path, help="use the catalog at this local directory")
    parser.add_argument("--allow-skill", dest="allowed", action="append", metavar="NAME",
                        help="admit this skill (repeat for every member of the permitted scope)")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    server = create_server(args.catalog_root or catalog_root(), allowed=args.allowed)
    if args.transport == "streamable-http":
        server.run(transport="streamable-http", host="127.0.0.1", port=args.port,
                   streamable_http_path="/mcp", stateless_http=True, json_response=True)
    else:
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
# ratios: loc_comments=76:15 imports_exports=10:2 calls_definitions=37:12
