from aios.verification.requirement_evidence import (
    EvidenceLink,
    MappingReport,
    Requirement,
    RequirementEvidenceMapper,
)
from aios.verification._common import VerificationError


def test_requirement_construction_immutable():
    r = Requirement("R1", "system shall log")
    assert r.requirement_id == "R1"
    assert r.text == "system shall log"


def test_map_requirement_pass_with_full_coverage():
    m = RequirementEvidenceMapper()
    r = Requirement("R1", "text")
    links = [EvidenceLink("L1", "R1", "E1"), EvidenceLink("L2", "R1", "E2")]
    rep = m.map_requirement(r, ["E1", "E2"], links=links)
    assert isinstance(rep, MappingReport)
    assert rep.coverage_ratio == 1.0
    assert rep.status == "PASS"


def test_map_requirement_insufficient_coverage():
    m = RequirementEvidenceMapper()
    r = Requirement("R1", "text")
    rep = m.map_requirement(r, ["E1", "E2", "E3", "E4"], links=[])
    assert rep.coverage_ratio == 0.0
    assert rep.status == "INSUFFICIENT"


def test_map_requirement_unknown_when_no_evidence():
    m = RequirementEvidenceMapper()
    r = Requirement("R1", "text")
    rep = m.map_requirement(r, [])
    assert rep.status == "UNKNOWN"


def test_map_requirement_rejects_empty_evidence_ref():
    m = RequirementEvidenceMapper()
    r = Requirement("R1", "text")
    try:
        m.map_requirement(r, ["E1", ""])
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_map_requirement_rejects_non_requirement():
    m = RequirementEvidenceMapper()
    try:
        m.map_requirement("not-a-requirement", ["E1"])
        assert False, "expected VerificationError"
    except VerificationError:
        pass


def test_map_requirement_deterministic_report_id():
    m = RequirementEvidenceMapper()
    r = Requirement("R1", "text")
    a = m.map_requirement(r, ["E1", "E2"])
    b = m.map_requirement(r, ["E1", "E2"])
    assert a.report_id == b.report_id
