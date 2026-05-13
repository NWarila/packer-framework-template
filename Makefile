PYTHON ?= python3

.PHONY: help setup clean fmt fmt-check init plugin-provenance plugin-install-check validate inspect ruff yamllint test workflow-helper-tests opa-test opa-policy opa-artifact manifest-check docs docs-diff docs-layout adr-schema lint policy docs-check integration ci verify verify-clean

help:
	@printf "Targets:\n"
	@printf "  setup          Install local Python lint dependencies\n"
	@printf "  clean          Remove generated Packer evidence\n"
	@printf "  lint           Run Packer, Python, and YAML checks\n"
	@printf "  test           Run fast local renderer assertions\n"
	@printf "  policy         Run OPA tests plus source and artifact policy evaluation\n"
	@printf "  docs-check     Check generated-doc drift, docs layout, and ADR schema\n"
	@printf "  integration    Run the credential-free reference Packer build\n"
	@printf "  ci             Run the repo-local quality gate\n"
	@printf "  verify         Run ci plus integration\n"
	@printf "  verify-clean   Clean generated evidence, then run verify\n"

setup:
	$(PYTHON) -m pip install --upgrade pyyaml==6.0.3 ruff==0.13.0 yamllint==1.35.1

clean:
	find packer/artifacts -mindepth 1 -maxdepth 1 ! -name .gitkeep -exec rm -rf {} +
	find packer/manifests -mindepth 1 -maxdepth 1 ! -name .gitkeep -exec rm -rf {} +

fmt:
	packer fmt -recursive packer examples

fmt-check:
	packer fmt -check -recursive packer examples

init:
	packer init packer

plugin-provenance:
	$(PYTHON) tools/verify.py plugin-provenance

plugin-install-check:
	$(PYTHON) tools/verify.py plugin-install-check

validate:
	packer validate -var-file examples/linux/reference-linux.pkrvars.hcl packer

inspect:
	packer inspect packer

ruff:
	$(PYTHON) tools/verify.py ruff

yamllint:
	$(PYTHON) tools/verify.py yamllint

test:
	$(PYTHON) tools/verify.py test

workflow-helper-tests:
	$(PYTHON) tools/verify.py workflow-helper-tests

opa-test:
	opa test policies/opa

opa-policy:
	$(PYTHON) tools/verify.py opa-policy

opa-artifact:
	$(PYTHON) tools/verify.py opa-artifact

manifest-check:
	$(PYTHON) tools/verify.py manifest-check

docs:
	$(PYTHON) tools/verify.py docs

docs-diff:
	$(PYTHON) tools/verify.py docs-diff

docs-layout:
	$(PYTHON) tools/verify.py docs-layout

adr-schema:
	$(PYTHON) tools/verify.py adr-schema

lint:
	$(MAKE) fmt-check
	$(MAKE) init
	$(MAKE) plugin-provenance
	$(MAKE) plugin-install-check
	$(MAKE) validate
	$(MAKE) inspect
	$(MAKE) ruff
	$(MAKE) yamllint

policy:
	$(MAKE) opa-test
	$(MAKE) opa-policy
	$(MAKE) opa-artifact

docs-check:
	$(MAKE) docs-diff
	$(MAKE) docs-layout
	$(MAKE) adr-schema

integration:
	$(PYTHON) tools/verify.py integration

ci:
	$(PYTHON) tools/verify.py ci

verify:
	$(PYTHON) tools/verify.py verify

verify-clean:
	$(MAKE) clean
	$(MAKE) verify
