
build:
	docker build -t python-showcase .

run: build
	docker run --name python-showcase --rm -p 9000:80 python-showcase

test: build
	docker run --name python-showcase --rm python-showcase python -m pytest /app/tests
