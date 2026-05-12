PYTHON ?= python3

.PHONY: help setup fmt fmt-check init validate inspect ruff yamllint opa-test opa-policy manifest-check docs-layout adr-schema lint policy docs-check integration ci verify

help:
	@printf "Targets:\n"
	@printf "  setup          Install local Python lint dependencies\n"
	@printf "  lint           Run Packer, Python, and YAML checks\n"
	@printf "  policy         Run OPA tests and source policy evaluation\n"
	@printf "  docs-check     Check docs layout and ADR schema\n"
	@printf "  integration    Run the credential-free reference Packer build\n"
	@printf "  ci             Run the repo-local quality gate\n"
	@printf "  verify         Run ci plus integration\n"

setup:
	$(PYTHON) -m pip install --upgrade pyyaml==6.0.3 ruff==0.13.0 yamllint==1.35.1

fmt:
	packer fmt -recursive packer examples

fmt-check:
	packer fmt -check -recursive packer examples

init:
	packer init packer

validate:
	packer validate -var-file=examples/linux/reference-linux.pkrvars.hcl packer

inspect:
	packer inspect packer

ruff:
	$(PYTHON) tools/verify.py ruff

yamllint:
	$(PYTHON) tools/verify.py yamllint

opa-test:
	opa test policies/opa

opa-policy:
	$(PYTHON) tools/verify.py opa-policy

manifest-check:
	$(PYTHON) tools/verify.py manifest-check

docs-layout:
	$(PYTHON) tools/verify.py docs-layout

adr-schema:
	$(PYTHON) tools/verify.py adr-schema

lint:
	$(MAKE) fmt-check
	$(MAKE) init
	$(MAKE) validate
	$(MAKE) inspect
	$(MAKE) ruff
	$(MAKE) yamllint

policy:
	$(MAKE) opa-test
	$(MAKE) opa-policy

docs-check:
	$(MAKE) docs-layout
	$(MAKE) adr-schema

integration:
	$(PYTHON) tools/verify.py integration

ci:
	$(PYTHON) tools/verify.py ci

verify:
	$(PYTHON) tools/verify.py verify
