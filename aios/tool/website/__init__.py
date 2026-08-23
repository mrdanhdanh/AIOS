"""AIOS website tool layer (TASK-223).

Layering: ``tool`` layer — stdlib + ``aios.core`` only. Never imports
``runtime`` / ``agent`` / ``orchestrator`` / ``capability``. The builder below
writes static site files; it is invoked through a Capability registered
elsewhere, proving the deliverable is produced BY AIOS rather than by hand.
"""

from .n5_builder import N5SiteBuilder, build_n5_site

__all__ = ["N5SiteBuilder", "build_n5_site"]
