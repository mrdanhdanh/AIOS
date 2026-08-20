"""Tests for System Catalog — AC-009-06/09/10 + search."""

import pytest

from aios.capability.catalog import CatalogEntry, CatalogError, SystemCatalog


def _entry(cat_type="capability", oid="execute_code", desc="Exec code", tags=None, source="capability-registry", meta=None):
    return CatalogEntry.create(
        catalog_type=cat_type,
        original_id=oid,
        description=desc,
        tags=tags or [],
        source=source,
        provenance={"producer": "test"},
        metadata=meta or {},
    )


# -- Validation --

def test_catalog_entry_minimal():
    e = _entry()
    e.validate()
    d = e.to_dict()
    assert d["source"] == "capability-registry"
    assert d["provenance"]["producer"] == "test"


def test_catalog_entry_invalid():
    with pytest.raises(CatalogError):
        CatalogEntry.create(catalog_type="", original_id="x")
    with pytest.raises(CatalogError):
        CatalogEntry.create(catalog_type="capability", original_id="")
    with pytest.raises(CatalogError):
        CatalogEntry.create(catalog_type="capability", original_id="x", tags=[""])


# -- AC-009-06: index + search by id/type/tag/query --

def test_catalog_index_and_list():
    cat = SystemCatalog()
    cat.index(_entry(oid="execute_code"))
    cat.index(_entry(oid="run_tests", cat_type="tool", source="tool-registry"))
    assert len(cat) == 2
    assert len(cat.list()) == 2


def test_catalog_duplicate_reject():
    cat = SystemCatalog()
    cat.index(_entry(oid="dup", cat_type="capability"))
    with pytest.raises(CatalogError):
        cat.index(_entry(oid="dup", cat_type="capability"))


def test_catalog_find_by_id():
    cat = SystemCatalog()
    cat.index(_entry(oid="execute_code", cat_type="capability"))
    cat.index(_entry(oid="execute_code", cat_type="tool"))
    results = cat.find_by_id("execute_code")
    assert len(results) == 2
    # case insensitive
    assert len(cat.find_by_id("EXECUTE_CODE")) == 2


def test_catalog_find_by_type():
    cat = SystemCatalog()
    cat.index(_entry(oid="a", cat_type="capability"))
    cat.index(_entry(oid="b", cat_type="prompt"))
    cat.index(_entry(oid="c", cat_type="capability"))
    caps = cat.find_by_type("capability")
    assert len(caps) == 2
    assert len(cat.find_by_type("CAPABILITY")) == 2


def test_catalog_find_by_tag():
    cat = SystemCatalog()
    cat.index(_entry(oid="cap1", tags=["exec", "runtime"]))
    cat.index(_entry(oid="cap2", tags=["test"]))
    assert len(cat.find_by_tag("exec")) == 1
    assert len(cat.find_by_tag("EXEC")) == 1
    assert len(cat.find_by_tag("missing")) == 0


def test_catalog_search_query():
    cat = SystemCatalog()
    cat.index(_entry(oid="execute_code", desc="Execute Python code", tags=["exec"]))
    cat.index(_entry(oid="analyze_code", desc="Analyze code"))
    results = cat.search("execute_code")
    assert any(r.original_id == "execute_code" for r in results)
    # description search
    results2 = cat.search("Python")
    assert len(results2) == 1
    # metadata search
    cat2 = SystemCatalog()
    cat2.index(_entry(oid="m1", cat_type="model", meta={"provider": "openai"}))
    assert len(cat2.search("openai")) == 1


def test_catalog_search_empty_reject():
    cat = SystemCatalog()
    with pytest.raises(CatalogError):
        cat.search("")
    with pytest.raises(CatalogError):
        cat.search("  ")


def test_catalog_upsert_replaces():
    cat = SystemCatalog()
    e1 = _entry(oid="cap_up", desc="v1")
    cat.index(e1)
    e2 = CatalogEntry.create(catalog_type="capability", original_id="cap_up", description="v2", source="capability-registry")
    cat.upsert(e2)
    assert len(cat) == 1
    assert cat.find_by_id("cap_up")[0].description == "v2"


def test_catalog_get_and_remove():
    cat = SystemCatalog()
    e = _entry(oid="to_remove")
    cat.index(e)
    fetched = cat.get(e.entry_id)
    assert fetched.original_id == "to_remove"
    cat.remove(entry_id=e.entry_id)
    assert len(cat) == 0
    with pytest.raises(CatalogError):
        cat.get(e.entry_id)


def test_catalog_remove_by_type_id():
    cat = SystemCatalog()
    cat.index(_entry(oid="rm_by_key", cat_type="capability"))
    cat.remove(catalog_type="capability", original_id="rm_by_key")
    assert len(cat) == 0


def test_catalog_remove_unknown():
    cat = SystemCatalog()
    with pytest.raises(CatalogError):
        cat.remove(entry_id="ghost")
    with pytest.raises(CatalogError):
        cat.remove(catalog_type="capability", original_id="ghost")


def test_catalog_contains_and_clear():
    cat = SystemCatalog()
    e = _entry(oid="check")
    cat.index(e)
    assert e.entry_id in cat
    cat.clear()
    assert len(cat) == 0


def test_catalog_sort_deterministic():
    cat = SystemCatalog()
    cat.index(_entry(oid="zebra", cat_type="capability"))
    cat.index(_entry(oid="apple", cat_type="capability"))
    listed = cat.list()
    assert listed[0].original_id == "apple"
    assert listed[1].original_id == "zebra"
    # search also sorted
    results = cat.search("a")
    ids = [r.original_id for r in results]
    assert ids == sorted(ids)


# -- AC-009-09 provenance --

def test_catalog_provenance_retained():
    cat = SystemCatalog()
    e = CatalogEntry.create(
        catalog_type="capability",
        original_id="prov_cap",
        source="capability-registry",
        provenance={"run_id": "run-123", "task_id": "TASK-009"},
    )
    cat.index(e)
    fetched = cat.get(e.entry_id)
    assert fetched.source == "capability-registry"
    assert fetched.provenance["run_id"] == "run-123"


def test_catalog_index_non_entry_reject():
    cat = SystemCatalog()
    with pytest.raises(CatalogError):
        cat.index("not-an-entry")  # type: ignore
