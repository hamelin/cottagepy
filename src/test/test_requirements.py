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


@pytest.mark.parametrize(
    "existing",
    [
        [],
        ["requests>=2.32", "pandas>3"],
    ],
)
def test_set_requirements(db: Database, existing: list[str]) -> None:
    for req in existing:
        modules.put_requirement(db, req)
    modules.set_requirements(
        db,
        """\
        numpy
        scipy>1.11 requests<2.3
        xarray>=2026.2.0
        requests>=2.22
        """
    )
    assert [Requirement(r) for r in ["numpy", "scipy>1.11", "requests>=2.22", "xarray>=2026.2.0"]
            ] == modules.get_requirements(db)
