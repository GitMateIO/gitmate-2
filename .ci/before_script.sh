export TEST_IMAGE_NAME=registry.gitlab.com/$CI_PROJECT_PATH:$CI_COMMIT_SHA
export MASTER_NAME=registry.gitlab.com/$CI_PROJECT_PATH:latest
export RELEASE_NAME=registry.gitlab.com/$CI_PROJECT_PATH:release
export WEBHOOK_SECRET=foobar
export COALA_RESULTS_IMAGE=registry.gitlab.com/gitmate/open-source/coala-incremental-results:latest
export RESULTS_BOUNCER_IMAGE=registry.gitlab.com/gitmate/open-source/result-bouncer:latest
export REBASER_IMAGE=registry.gitlab.com/gitmate/open-source/mr-rebaser:latest
export BOT_TOKEN=foobar
export BOT_USER=foo
export EE_PLUGINS=$(./docker/list-ee-plugins.sh)
echo "EE plugins found: $EE_PLUGINS"
