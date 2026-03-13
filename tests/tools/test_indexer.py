from insightforge.tools.indexer import build_index_id


def test_build_index_id_consistent():
    id1 = build_index_id("/home/user/project")
    id2 = build_index_id("/home/user/project")
    assert id1 == id2


def test_build_index_id_different_folders():
    id1 = build_index_id("/home/user/project_a")
    id2 = build_index_id("/home/user/project_b")
    assert id1 != id2


def test_build_index_id_is_string():
    result = build_index_id("/any/path")
    assert isinstance(result, str)
    assert len(result) > 0
