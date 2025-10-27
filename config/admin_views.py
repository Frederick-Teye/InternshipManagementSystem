from __future__ import annotations

import os
from pathlib import Path

from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.urls import path


@staff_member_required
def log_files_list(request):
    """List available log files for download."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        log_files = []
    else:
        log_files = [
            {
                "name": f.name,
                "path": f,
                "size": f.stat().st_size,
                "modified": f.stat().st_mtime,
            }
            for f in logs_dir.iterdir()
            if f.is_file() and f.name.endswith(".log")
        ]
        # Sort by modification time, newest first
        log_files.sort(key=lambda x: x["modified"], reverse=True)

    return render(
        request,
        "admin/log_files_list.html",
        {
            "log_files": log_files,
            "title": "Log Files",
        },
    )


@staff_member_required
def download_log_file(request, filename):
    """Download a specific log file."""
    logs_dir = Path("logs")
    file_path = logs_dir / filename

    # Security check: only allow .log files and prevent directory traversal
    if not filename.endswith(".log") or ".." in filename or not file_path.exists():
        raise Http404("Log file not found")

    try:
        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="text/plain",
        )
    except IOError:
        raise Http404("Unable to read log file")


# URL patterns for log file management
log_urls = [
    path("logs/", log_files_list, name="log_files_list"),
    path("logs/download/<str:filename>/", download_log_file, name="download_log_file"),
]
