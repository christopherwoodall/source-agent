#!/usr/bin/make -f
# -*- makefile -*-

SHELL         := /bin/bash
.SHELLFLAGS   := -eu -o pipefail -c
.DEFAULT_GOAL := help
.LOGGING      := 0

.ONESHELL:             ;	# Recipes execute in same shell
.NOTPARALLEL:          ;	# Wait for this target to finish
.SILENT:               ;	# No need for @
.EXPORT_ALL_VARIABLES: ;	# Export variables to child processes.
.DELETE_ON_ERROR:      ;	# Delete target if recipe fails.

# Modify the block character to be `-\t` instead of `\t`
ifeq ($(origin .RECIPEPREFIX), undefined)
	$(error This version of Make does not support .RECIPEPREFIX.)
endif
.RECIPEPREFIX = -


PROJECT_DIR := $(shell git rev-parse --show-toplevel)
SRC_DIR     := $(PROJECT_DIR)/src
BUILD_DIR   := $(PROJECT_DIR)/dist

default: $(.DEFAULT_GOAL)
all: help


define Bandit
	bandit                  \
		-v                  \
		-f txt              \
		-r $1               \
		-c "pyproject.toml"
endef


.PHONY: help
help: ## List commands <default>
-	echo -e "USAGE: make \033[36m[COMMAND]\033[0m\n"
-	echo "Available commands:"
-	awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\t\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


.PHONY: build
build: ## Build the application
-	pip install wheel
-	pip install --upgrade pip wheel
-	pip install --editable ".[developer]"
-	hatch build --clean --target wheel


.PHONY: run
run: ## Run the application
-	scenario-lab


.PHONY: lint
lint: ## Lint the code
-	black $(SRC_DIR)
-	ruff check $(SRC_DIR) --fix


.PHONY: bandit
bandit: ## Run bandit
-	$(call Bandit,./src)


.PHONY: test
test: ## Run the tests
-	pytest -s
