declare -a plugins=(
    "similar"
)


function clone_or_pull {
    if [ -d "gitmate_$1_ee" ]; then
        cd gitmate_$1_ee
        echo "Updating $1..."
        git pull
        cd ..
    else
        echo "Cloning $1..."
        git clone git@gitlab.com:gitmate/ee-plugins/$1.git gitmate_$1_ee
    fi
}

echo "Be sure to have a valid GitLab SSH key for pulling the GitMate EE repositories."

cd plugins

for plugin in "${plugins[@]}"
do
    clone_or_pull $plugin
done

cd ..
