git add .

NUM_YAML=$(git diff --staged --name-only | grep -oc "\.yaml")

if [ "$NUM_YAML" -gt "0" ]
then
  echo "Found $NUM_YAML yaml additions during testing..."
  echo $(git diff --staged --name-only | grep "\.yaml")
  exit 1
else
  exit 0
fi
