# Use make to install pip3 and then install our dependencies

all:
	wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py --user && export PATH="$PATH:~/.local/bin/" && \
	pip3 install --user -r requirements.txt