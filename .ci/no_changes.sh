git add .

NUM_CHANGES=$(git diff --name-only | egrep -oc "\.yaml|\.py|_ee")

if [ "$NUM_CHANGES" -gt "0" ]
then
  echo "Found $NUM_CHANGES additions during testing..."
  echo $(git diff --name-only | egrep -o "\.yaml|\.py|_ee")
  exit 1
else
  exit 0
fi
