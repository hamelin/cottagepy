UV_RUN = uv run --dev


all: test type pep8

tests: test

test: reformat
	$(UV_RUN) pytest $(and $(dbg),--last-failed --trace) $(and $(failfast),-x) $(and $(pdb),--pdb) $(and $(only),-k "$(only)") src

type: reformat
	$(UV_RUN) mypy --ignore-missing-imports src

pep8: reformat
	$(UV_RUN) flake8 src

reformat:
	$(UV_RUN) yapf -impr src
