DOCKER="docker"
IMAGE_NAME="kiansheik/muscogee"
TAG_NAME="production"

REPOSITORY=""
FULL_IMAGE_NAME=${IMAGE_NAME}:${TAG_NAME}

lint:
	zsh -c 'cd mvskoke; python3.11 setup.py sdist bdist_wheel;'
	echo 'kiansheik.io' > CNAME
	black .

push:
	make lint
	git add .
	git commit
	git push origin HEAD

gen_data:
	python3.11 ankigen_muscogee.py
	python3 mvskoke/tests/context.py