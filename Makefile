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
-	source-agent


.PHONY: lint
lint: ## Lint the code
-	black $(SRC_DIR)
-	ruff check $(SRC_DIR) --fix


.PHONY: bandit
bandit: ## Run bandit
-	bandit --config $(PROJECT_DIR)/pyproject.toml --recursive . --verbose
# -	bandit --config $(PROJECT_DIR)/pyproject.toml --recursive . --verbose --format html --output bandit_report.html

.PHONY: test
test: ## Run the tests
-	pytest -s


.PHONY: test-tools
test-tools: ## Run tool CRUDE tests
# CREATE
-	source-agent --prompt "create a directory called 'test'"
# READ
-	source-agent --prompt "summarize the project readme"
-	source-agent --prompt "list all files in the project root directory" 
-	source-agent --prompt "find all the files that import 'registry'" 
# UPDATE
-	source-agent --prompt "write the words 'test' to a file named 'test/testing.txt'"
# DELETE
-	source-agent --prompt "delete the file 'test/testing.txt'"
-	source-agent --prompt "delete the directory 'test'"
# EXECUTE
-	source-agent --prompt "calculate (9+1)*6/2"
-	source-agent --prompt "search the web for how to create a virtual environment with 'uv'" 
