.PHONY: test image smoke scan source-scan

IMAGE_NAME ?= base
ARCH ?= $(shell uname -m | sed 's/aarch64/arm64/;s/x86_64/amd64/')
IMAGE ?= hadou-base-images:$(IMAGE_NAME)-$(ARCH)
OUTPUT ?= out/$(IMAGE_NAME)/$(ARCH)
DOCKERFILE = $(shell python3 scripts/catalog.py field $(IMAGE_NAME) dockerfile)
PROFILE = $(shell python3 scripts/catalog.py field $(IMAGE_NAME) profile)

test:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
	bash -n scripts/*.sh

image:
	docker build --platform linux/$(ARCH) --pull --no-cache -f $(DOCKERFILE) -t $(IMAGE) .

smoke:
	bash scripts/container_smoke.sh $(IMAGE) $(IMAGE_NAME)

scan:
	mkdir -p $(OUTPUT)
	docker save $(IMAGE) -o $(OUTPUT)/image.tar
	bash scripts/sha256.sh $(OUTPUT)/image.tar > $(OUTPUT)/image.tar.sha256
	python3 scripts/scan.py image $(OUTPUT)/image.tar --profile $(PROFILE) --output $(OUTPUT)/security

source-scan:
	python3 scripts/scan.py source . --output out/source-security
