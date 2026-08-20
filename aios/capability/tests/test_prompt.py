"""Tests for Prompt Registry — AC-009-04/05/10 + version + rendering."""

import threading
import pytest

from aios.capability.prompt import PromptContract, PromptError, PromptRegistry


# -- Contract --

def test_prompt_create_minimal():
    p = PromptContract.create("code_review", "Review {file}", version="1.0.0")
    assert p.prompt_id == "code_review"
    assert p.variables == ["file"]
    assert p.render(file="main.py") == "Review main.py"


def test_prompt_version_validation():
    with pytest.raises(PromptError):
        PromptContract.create("p1", "Hello {x}", version="bad")


def test_prompt_id_validation():
    with pytest.raises(PromptError):
        PromptContract.create("", "Hello {x}")
    with pytest.raises(PromptError):
        PromptContract.create("123bad", "Hello {x}")


def test_prompt_invalid_placeholder():
    with pytest.raises(PromptError):
        PromptContract.create("p1", "Hello {123bad}")


def test_prompt_missing_variable_fail():
    p = PromptContract.create("greet", "Hello {name}, you are {role}")
    with pytest.raises(PromptError, match="Missing variables"):
        p.render(name="Alice")
    with pytest.raises(PromptError):
        p.render()


def test_prompt_extra_variable_ignored():
    p = PromptContract.create("greet2", "Hello {name}")
    assert p.render(name="Bob", extra="ignored") == "Hello Bob"


def test_prompt_no_variables():
    p = PromptContract.create("plain", "Hello world")
    assert p.variables == []
    assert p.render() == "Hello world"


def test_prompt_multiple_variables():
    p = PromptContract.create("multi", "A {x} B {y} C {x}")
    assert sorted(p.variables) == ["x", "x", "y"] or set(p.variables) == {"x", "y"}
    assert p.render(x="1", y="2") == "A 1 B 2 C 1"


def test_prompt_provenance_retained():
    p = PromptContract.create("p_prov", "Hi {x}", source="prompt-registry", metadata={"team": "ai"})
    d = p.to_dict()
    assert d["source"] == "prompt-registry"
    assert d["metadata"]["team"] == "ai"


def test_prompt_to_dict_roundtrip():
    p = PromptContract.create("p_dict", "Val {v}", version="1.2.3", description="desc")
    d = p.to_dict()
    assert d["prompt_id"] == "p_dict"
    assert d["version"] == "1.2.3"


# -- Registry AC-009-04/05 --

def test_registry_version_lookup():
    reg = PromptRegistry()
    reg.register(PromptContract.create("code_review", "Review {file}", version="1.0.0"))
    reg.register(PromptContract.create("code_review", "Review v2 {file} in {lang}", version="1.1.0"))
    # explicit version
    assert reg.get("code_review", version="1.0.0").template == "Review {file}"
    assert reg.get("code_review", version="1.1.0").template == "Review v2 {file} in {lang}"
    # latest without version
    assert reg.get("code_review").version == "1.1.0"
    assert reg.versions("code_review") == ["1.0.0", "1.1.0"]


def test_registry_render():
    reg = PromptRegistry()
    reg.register(PromptContract.create("summarize", "Summarize {doc}", version="1.0.0"))
    assert reg.render("summarize", doc="hello") == "Summarize hello"


def test_registry_render_versioned():
    reg = PromptRegistry()
    reg.register(PromptContract.create("p_r", "Hello {name}", version="1.0.0"))
    reg.register(PromptContract.create("p_r", "Hi {name}!", version="2.0.0"))
    assert reg.render("p_r", version="1.0.0", name="A") == "Hello A"
    assert reg.render("p_r", version="2.0.0", name="A") == "Hi A!"


def test_registry_missing_variable_fail():
    reg = PromptRegistry()
    reg.register(PromptContract.create("need_var", "Need {x}"))
    with pytest.raises(PromptError):
        reg.render("need_var")


def test_registry_duplicate_reject():
    reg = PromptRegistry()
    reg.register(PromptContract.create("dup_p", "Hi {x}", version="1.0.0"))
    with pytest.raises(PromptError):
        reg.register(PromptContract.create("dup_p", "Hi {x} v2", version="1.0.0"))


def test_registry_unknown_reject():
    reg = PromptRegistry()
    with pytest.raises(PromptError):
        reg.get("no_such")
    with pytest.raises(PromptError):
        reg.versions("no_such")
    with pytest.raises(PromptError):
        reg.render("no_such", x="a")


def test_registry_list_and_contains():
    reg = PromptRegistry()
    reg.register(PromptContract.create("p_a", "A {x}", version="1.0.0"))
    reg.register(PromptContract.create("p_b", "B {y}", version="1.0.0"))
    assert len(reg) == 2
    assert "p_a" in reg
    assert "missing" not in reg
    all_prompts = reg.list()
    assert len(all_prompts) == 2
    # filter by prompt_id
    assert len(reg.list("p_a")) == 1


def test_registry_remove():
    reg = PromptRegistry()
    reg.register(PromptContract.create("to_remove", "Hi {x}", version="1.0.0"))
    reg.register(PromptContract.create("to_remove", "Hi {x} v2", version="2.0.0"))
    reg.remove("to_remove", version="1.0.0")
    assert reg.versions("to_remove") == ["2.0.0"]
    reg.remove("to_remove")
    assert "to_remove" not in reg


def test_registry_remove_unknown():
    reg = PromptRegistry()
    with pytest.raises(PromptError):
        reg.remove("ghost")
    reg.register(PromptContract.create("p_x", "Hello {a}", version="1.0.0"))
    with pytest.raises(PromptError):
        reg.remove("p_x", version="9.9.9")


def test_registry_clear():
    reg = PromptRegistry()
    reg.register(PromptContract.create("p_cl", "Hi {x}"))
    reg.clear()
    assert len(reg) == 0


def test_registry_register_non_contract_reject():
    reg = PromptRegistry()
    with pytest.raises(PromptError):
        reg.register("not-a-contract")  # type: ignore


# -- Thread safety --

def test_thread_safety_concurrent_register():
    reg = PromptRegistry()
    errors = []

    def worker(idx: int):
        try:
            p = PromptContract.create(f"p_{idx}", "Val {x}", version="1.0.0")
            reg.register(p)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(15)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert len(reg) == 15
