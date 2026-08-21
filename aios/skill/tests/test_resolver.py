"""Tests for Skill Dependency Resolver — AC-015-02 (TASK-015)."""

import pytest

from aios.skill.contracts import SkillContract, SkillDependency
from aios.skill.registry import SkillRegistry
from aios.skill.resolver import DependencyGraph, ResolverError, SkillDependencyResolver


def _contract(skill_id, version="1.0.0", deps=None, **kwargs):
    deps_list = []
    for d in deps or []:
        if isinstance(d, str):
            deps_list.append(SkillDependency(skill_id=d, version_constraint=">=1.0.0"))
        elif isinstance(d, dict):
            deps_list.append(SkillDependency.from_dict(d))
        else:
            deps_list.append(d)
    return SkillContract.create(
        skill_id=skill_id,
        version=version,
        entrypoint="skill.main:run",
        dependencies=deps_list,
        **kwargs,
    )


def test_resolve_no_deps():
    reg = SkillRegistry()
    reg.register(_contract("skill-a"))
    resolver = SkillDependencyResolver(registry=reg)
    result = resolver.resolve("skill-a")
    assert result.is_success
    assert "skill-a" in result.resolved
    assert result.skill_id == "skill-a"


def test_resolve_direct_dep():
    reg = SkillRegistry()
    reg.register(_contract("skill-b"))
    reg.register(_contract("skill-a", deps=["skill-b"]))
    resolver = SkillDependencyResolver(registry=reg)
    result = resolver.resolve("skill-a")
    assert result.is_success
    assert "skill-b" in result.resolved
    # Topological order: dependency before dependent
    assert result.order.index("skill-b") < result.order.index("skill-a")


def test_resolve_transitive():
    reg = SkillRegistry()
    reg.register(_contract("skill-d", version="3.0.0"))
    reg.register(_contract("skill-c", version="2.0.0"))
    reg.register(_contract("skill-b", deps=[{"skill_id": "skill-d", "version_constraint": ">=3.0.0"}]))
    reg.register(_contract("skill-a", deps=[
        {"skill_id": "skill-b", "version_constraint": ">=1.0.0"},
        {"skill_id": "skill-c", "version_constraint": ">=2.0.0"},
    ]))
    resolver = SkillDependencyResolver(registry=reg)
    result = resolver.resolve("skill-a")
    assert result.is_success
    assert set(result.resolved) == {"skill-a", "skill-b", "skill-c", "skill-d"}
    # Check topological order
    assert result.order.index("skill-d") < result.order.index("skill-b")
    assert result.order.index("skill-b") < result.order.index("skill-a")
    assert result.order.index("skill-c") < result.order.index("skill-a")


def test_resolve_missing_dep():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", deps=["skill-b"]))
    resolver = SkillDependencyResolver(registry=reg)
    with pytest.raises(ResolverError, match="Missing"):
        resolver.resolve("skill-a")


def test_resolve_version_conflict():
    reg = SkillRegistry()
    reg.register(_contract("skill-b", version="1.0.0"))
    reg.register(_contract("skill-a", deps=[{"skill_id": "skill-b", "version_constraint": ">=2.0.0"}]))
    resolver = SkillDependencyResolver(registry=reg)
    with pytest.raises(ResolverError, match="conflict"):
        resolver.resolve("skill-a")


def test_resolve_cycle():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", deps=["skill-b"]))
    reg.register(_contract("skill-b", deps=["skill-c"]))
    reg.register(_contract("skill-c", deps=["skill-a"]))
    resolver = SkillDependencyResolver(registry=reg)
    with pytest.raises(ResolverError, match="Circular"):
        resolver.resolve("skill-a")


def test_resolve_self_cycle():
    reg = SkillRegistry()
    # Self-dependency should be caught
    c = _contract("skill-a", deps=["skill-a"])
    reg.register(c)
    resolver = SkillDependencyResolver(registry=reg)
    with pytest.raises(ResolverError):
        resolver.resolve("skill-a")


def test_resolve_unknown_skill():
    reg = SkillRegistry()
    resolver = SkillDependencyResolver(registry=reg)
    with pytest.raises(ResolverError, match="Unknown"):
        resolver.resolve("unknown")


def test_resolve_with_available():
    reg = SkillRegistry()
    reg.register(_contract("skill-b", version="1.0.0"))
    resolver = SkillDependencyResolver(registry=reg)
    # skill-a not in registry but in available
    available = {"skill-a": _contract("skill-a", deps=["skill-b"])}
    result = resolver.resolve("skill-a", available=available)
    assert result.is_success


def test_check_compatibility():
    reg = SkillRegistry()
    reg.register(_contract("skill-b", version="1.0.0"))
    reg.register(_contract("skill-a", deps=[{"skill_id": "skill-b", "version_constraint": ">=1.0.0"}]))
    resolver = SkillDependencyResolver(registry=reg)
    assert resolver.check_compatibility("skill-a") is True
    reg2 = SkillRegistry()
    reg2.register(_contract("skill-b", version="1.0.0"))
    reg2.register(_contract("skill-a", deps=[{"skill_id": "skill-b", "version_constraint": ">=2.0.0"}]))
    resolver2 = SkillDependencyResolver(registry=reg2)
    assert resolver2.check_compatibility("skill-a") is False


def test_get_transitive():
    reg = SkillRegistry()
    reg.register(_contract("skill-c"))
    reg.register(_contract("skill-b", deps=["skill-c"]))
    reg.register(_contract("skill-a", deps=["skill-b"]))
    resolver = SkillDependencyResolver(registry=reg)
    trans = resolver.get_transitive_dependencies("skill-a")
    assert trans == {"skill-b", "skill-c"}


def test_has_cycle():
    reg = SkillRegistry()
    reg.register(_contract("skill-a", deps=["skill-b"]))
    reg.register(_contract("skill-b", deps=["skill-a"]))
    resolver = SkillDependencyResolver(registry=reg)
    assert resolver.has_cycle("skill-a") is True
    reg2 = SkillRegistry()
    reg2.register(_contract("skill-a"))
    resolver2 = SkillDependencyResolver(registry=reg2)
    assert resolver2.has_cycle("skill-a") is False


def test_dependency_graph():
    g = DependencyGraph()
    g.add_node("a")
    g.add_node("b")
    g.add_edge("a", "b")
    assert "b" in g.dependencies_of("a")
    assert g.get_closure("a") == {"b"}
    assert g.detect_cycle() is None
    g.add_edge("b", "a")
    assert g.detect_cycle() is not None
    # Topological sort should fail on cycle
    with pytest.raises(ResolverError):
        g.topological_sort()


def test_dependency_graph_topological():
    g = DependencyGraph()
    g.add_edge("a", "b")
    g.add_edge("a", "c")
    g.add_edge("b", "d")
    order = g.topological_sort()
    assert order.index("d") < order.index("b")
    assert order.index("b") < order.index("a")
    assert order.index("c") < order.index("a")


def test_resolve_version_constraint_tilde():
    reg = SkillRegistry()
    reg.register(_contract("skill-b", version="2.5.0"))
    reg.register(_contract("skill-a", deps=[{"skill_id": "skill-b", "version_constraint": "~=2.0"}]))
    resolver = SkillDependencyResolver(registry=reg)
    result = resolver.resolve("skill-a")
    assert result.is_success


def test_resolve_version_constraint_caret():
    reg = SkillRegistry()
    reg.register(_contract("skill-b", version="1.5.0"))
    reg.register(_contract("skill-a", deps=[{"skill_id": "skill-b", "version_constraint": "^1.2.3"}]))
    resolver = SkillDependencyResolver(registry=reg)
    result = resolver.resolve("skill-a")
    assert result.is_success
