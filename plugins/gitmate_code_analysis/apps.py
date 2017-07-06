from django.apps import AppConfig

from gitmate.utils import PluginCategory


class GitmateCodeAnalysisConfig(AppConfig):
    name = 'plugins.gitmate_code_analysis'
    verbose_name = 'Code Analysis'
    plugin_category = PluginCategory.ANALYSIS
    description = '''
<p>Checks new and updated pull requests of this repository
for new errors and bad practices. Issues introduced by the pull request in
question will be commented on directly in the diff of the pull request.</p>
<p>
The analysis uses <a href="https://coala.io">coala</a> and
<b> needs to be configured via a file named <code>.coafile</code> in your
repository, as described
<a href="https://docs.coala.io/en/latest/Users/Tutorial.html"> here<a/></b>.
</p>
<p>
An example <code>.coafile</code> for a python project could look like this:
</p>
<pre>
[all]
ignore = .git/**

[all.python]
files = *.py
ignore += **/__init__.py
bears = PEP8Bear, PyCommentedCodeBear, PyUnusedCodeBear
language = python
use_spaces = True
remove_all_unused_imports = True

[all.commit]
bears = GitCommitBear
shortlog_trailing_period = False
shortlog_regex = ([^:]*|[^:]+[^ ]: [A-Z0-9*].*)
</pre>
'''
