#
# Make file for the git-it project
#
all: archive

archive:
	@git archive --format=tar --prefix=/prj/git-it/ HEAD | gzip -9 > git-it.tar.gz
	@echo "built package 'git-it.tar.gz'"

clean:
	@find lib -type f -name '*.pyc' -exec rm {} \;
	@rm -f git-it.tar.gz
