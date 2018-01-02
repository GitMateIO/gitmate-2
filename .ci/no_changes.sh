git add .

NUM_CHANGES=$(git diff --staged --name-only | grep -oc "\.yaml|\.py")

if [ "$NUM_CHANGES" -gt "0" ]
then
  echo "Found $NUM_CHANGES additions during testing..."
  echo $(git diff --staged --name-only | grep -oc "\.yaml|\.py")
  exit 1
else
  exit 0
fi
