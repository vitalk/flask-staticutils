all: test clean


install:
	@python setup.py install


install-dev:
	@pip install -qr requirements.dev.txt


clean:
	@rm -rf build dist *.egg-info


test: install-dev
	@python setup.py test
