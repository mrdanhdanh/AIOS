"""Automated tests for the runtime context service (TASK-004)."""

import pytest

from aios.runtime.context import ContextError, ContextStore, ContextType, RuntimeContext


def test_six_context_types_present():
    types = {t.value for t in ContextType}
    assert types == {"request", "agent", "workflow", "capability", "tool", "execution"}


def test_context_create_mints_id():
    ctx = RuntimeContext.create(ContextType.AGENT, attributes={"agent_id": "a1"})
    assert ctx.context_id.startswith("ctx-")
    assert ctx.context_type == ContextType.AGENT
    assert ctx.get_attr("agent_id") == "a1"


def test_context_store_put_get():
    store = ContextStore()
    ctx = RuntimeContext.create(ContextType.REQUEST)
    store.put(ctx)
    assert store.get(ctx.context_id).context_type == ContextType.REQUEST
    assert store.exists(ctx.context_id)
    assert len(store) == 1


def test_context_store_get_missing_raises():
    store = ContextStore()
    with pytest.raises(ContextError):
        store.get("nope")


def test_context_store_list_by_type():
    store = ContextStore()
    a = RuntimeContext.create(ContextType.AGENT)
    b = RuntimeContext.create(ContextType.AGENT)
    c = RuntimeContext.create(ContextType.TOOL)
    for x in (a, b, c):
        store.put(x)
    agents = store.list_by_type(ContextType.AGENT)
    assert {x.context_id for x in agents} == {a.context_id, b.context_id}


def test_context_store_hierarchy_children():
    store = ContextStore()
    parent = RuntimeContext.create(ContextType.REQUEST)
    child = RuntimeContext.create(ContextType.AGENT, parent_id=parent.context_id)
    store.put(parent)
    store.put(child)
    kids = store.children_of(parent.context_id)
    assert [k.context_id for k in kids] == [child.context_id]


def test_context_store_resolve_chain():
    store = ContextStore()
    req = RuntimeContext.create(ContextType.REQUEST)
    agent = RuntimeContext.create(ContextType.AGENT, parent_id=req.context_id)
    cap = RuntimeContext.create(ContextType.CAPABILITY, parent_id=agent.context_id)
    tool = RuntimeContext.create(ContextType.TOOL, parent_id=cap.context_id)
    for x in (req, agent, cap, tool):
        store.put(x)
    chain = store.resolve_chain(tool.context_id)
    assert [c.context_type for c in chain] == [
        ContextType.TOOL,
        ContextType.CAPABILITY,
        ContextType.AGENT,
        ContextType.REQUEST,
    ]


def test_context_store_delete():
    store = ContextStore()
    ctx = RuntimeContext.create(ContextType.EXECUTION)
    store.put(ctx)
    store.delete(ctx.context_id)
    assert not store.exists(ctx.context_id)
    assert len(store) == 0


def test_context_store_rejects_non_context():
    store = ContextStore()
    with pytest.raises(ContextError):
        store.put("not-a-context")


def test_context_store_thread_safety():
    import threading

    store = ContextStore()
    barrier = threading.Barrier(8)

    def worker(i):
        barrier.wait()
        ctx = RuntimeContext.create(ContextType.TOOL, attributes={"i": i})
        store.put(ctx)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(store) == 8
