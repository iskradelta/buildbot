.PHONY: all reference cleanpyc

all: reference.tgz

cleanpyc:
	cd .. && find master worker -name '*.pyc' -exec rm \{} \; || exit 1

reference: cleanpyc
	rm -rf reference
	cd .. && python apidocs/epyrun -o apidocs/reference \
			--exclude="buildbot\\.test" --exclude="buildworker\\.test" \
			buildbot buildworker

reference.tgz: reference
	tar -zcf reference.tgz reference
