from packaging.requirements import Requirement
import pytest  # noqa

from cottagepy import Database, modules


@pytest.mark.parametrize(
    "reqs",
    [
        [],
        ["requests>=2.30"],
        ["pandas>=3", "numpy<2.3"],
    ],
)
def test_requirements(reqs: list[str], db: Database) -> None:
    for req in reqs:
        modules.put_requirement(db, req)
    assert [Requirement(req) for req in reqs] == modules.get_requirements(db)


def test_replace_requirement(db: Database) -> None:
    modules.put_requirement(db, "requests>=2")
    modules.put_requirement(db, "pandas>=3")
    assert [Requirement("requests>=2"), Requirement("pandas>=3")] == modules.get_requirements(db)
    modules.put_requirement(db, "requests>=2.32")
    assert [Requirement("requests>=2.32"),
            Requirement("pandas>=3")] == modules.get_requirements(db)
