#!/bin/sh

scan() {
    echo "Running TFLint..."
    tflint --color --chdir .

    echo "Running TFSec..."
    tfsec .

    echo "Running Terrascan..."
    terrascan init
    terrascan scan .
}

# If no argument is provided, start scanning.
if [ "$#" -ne 1 ]; then
    scan
elif [ "$1" == "sh" ]; then
    echo "Initiating shell..."
    /bin/sh -i
elif [[ "$1" == http://* || "$1" == https://* ]]; then
    git clone "$1" repo
    cd repo || { echo "Failed to change to the 'repo' directory"; exit 1; }
    scan
else
    echo "Invalid argument."
    echo "Usage: docker run hadou.io/tfmux (For starting the scan in the current directory)"
    echo "       docker run -it hadou.io/tfmux sh (For shell mode)"
    echo "       docker run hadou.io/tfmux <git-repo-url> (For automatic clone and run scan)"
    exit 1
fi
