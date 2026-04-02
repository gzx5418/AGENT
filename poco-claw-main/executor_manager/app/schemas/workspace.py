from typing import Literal

from pydantic import BaseModel


class FileNode(BaseModel):
    id: str
    name: str
    type: Literal["file", "folder"]
    path: str
    children: list["FileNode"] | None = None
    mimeType: str | None = None


class WorkspaceExportResult(BaseModel):
    workspace_files_prefix: str | None = None
    workspace_manifest_key: str | None = None
    workspace_archive_key: str | None = None
    workspace_export_status: str = "failed"
    error: str | None = None
