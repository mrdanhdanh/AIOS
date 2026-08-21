"""Post-migration validation pipeline.

AC-020-07: Migration has validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ValidationStatus(str, Enum):
    """Status of a validation check."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class ValidationCheck:
    """Result of a single validation check."""
    name: str
    status: ValidationStatus
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "detail": self.detail,
        }


@dataclass
class ValidationResult:
    """Overall validation result."""
    passed: bool = True
    checks: list[ValidationCheck] = field(default_factory=list)
    failed_count: int = 0
    passed_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [c.to_dict() for c in self.checks],
            "failed_count": self.failed_count,
            "passed_count": self.passed_count,
        }


ValidationFunc = Callable[[dict[str, Any]], ValidationCheck]


class ValidationPipeline:
    """Runs post-migration validation checks.

    AC-020-07: Migration has validation.
    """

    def __init__(self) -> None:
        self._checks: list[tuple[str, ValidationFunc]] = []

    def register(self, name: str, check_fn: ValidationFunc) -> None:
        """Register a validation check."""
        self._checks.append((name, check_fn))

    def validate(self, state: dict[str, Any]) -> ValidationResult:
        """Run all validation checks."""
        results: list[ValidationCheck] = []
        for name, check_fn in self._checks:
            try:
                result = check_fn(state)
                results.append(result)
            except Exception as e:
                results.append(ValidationCheck(
                    name=name,
                    status=ValidationStatus.FAIL,
                    detail=f"Exception: {e}",
                ))

        failed = sum(1 for c in results if c.status == ValidationStatus.FAIL)
        passed = sum(1 for c in results if c.status == ValidationStatus.PASS)

        return ValidationResult(
            passed=failed == 0,
            checks=results,
            failed_count=failed,
            passed_count=passed,
        )

    def validate_with_manifest_checks(
        self,
        state: dict[str, Any],
        manifest_checks: list[str],
    ) -> ValidationResult:
        """Validate using manifest-specified check names."""
        results: list[ValidationCheck] = []
        for check_name in manifest_checks:
            found = False
            for name, check_fn in self._checks:
                if name == check_name:
                    try:
                        result = check_fn(state)
                        results.append(result)
                    except Exception as e:
                        results.append(ValidationCheck(
                            name=name,
                            status=ValidationStatus.FAIL,
                            detail=f"Exception: {e}",
                        ))
                    found = True
                    break
            if not found:
                results.append(ValidationCheck(
                    name=check_name,
                    status=ValidationStatus.SKIP,
                    detail=f"Check '{check_name}' not registered",
                ))

        failed = sum(1 for c in results if c.status == ValidationStatus.FAIL)
        passed = sum(1 for c in results if c.status == ValidationStatus.PASS)

        return ValidationResult(
            passed=failed == 0,
            checks=results,
            failed_count=failed,
            passed_count=passed,
        )
