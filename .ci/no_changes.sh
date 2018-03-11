git add .

NUM_CHANGES=$(git ls-files --other --modified --exclude-standard | egrep -oc "\.yaml|\.py|_ee")
CHANGES=$(git ls-files --other --modified --exclude-standard | egrep -o "\.yaml|\.py|_ee")

if [ "$NUM_CHANGES" -gt "0" ]
then
  echo "Found $NUM_CHANGES additions during testing..."
  echo $CHANGES
  exit 1
else
  exit 0
fi
