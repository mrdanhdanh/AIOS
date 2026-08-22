"""DevKit packaging — produces a checksummed artifact bundle."""

from __future__ import annotations

import hashlib
import json

from aios.devkit.manifest import DevKitManifest


class Packager:
    """Packages a manifest + files into a checksummed bundle."""

    def package(self, manifest: DevKitManifest, files: list[str]) -> dict:
        errors = manifest.validate()
        if errors:
            raise ValueError(f"Manifest invalid: {errors}")
        payload = json.dumps(
            {"manifest": manifest.to_dict(), "files": files},
            sort_keys=True,
        ).encode("utf-8")
        checksum = hashlib.sha256(payload).hexdigest()
        return {
            "name": manifest.name,
            "version": manifest.version,
            "files": files,
            "checksum": checksum,
        }
