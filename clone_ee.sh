declare -a plugins=(
    "hello_ee"
)


function clone_or_pull {
    if [ -d "gitmate_$1" ]; then
        cd gitmate_$1
        echo "Updating $1..."
        git pull
        cd ..
    else
        echo "Cloning $1..."
        git clone git@gitlab.com:gitmate/ee-plugins/$1.git gitmate_$1
    fi
}

echo "Be sure to have a valid GitLab SSH key for pulling the GitMate EE repositories."

cd plugins

for plugin in "${plugins[@]}"
do
    clone_or_pull $plugin
done

cd ..
