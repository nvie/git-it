#
# Make file for the git-it project
#
all: nothing

nothing:

clean:
	@find lib -type f -name '*.pyc' -exec rm {} \;
