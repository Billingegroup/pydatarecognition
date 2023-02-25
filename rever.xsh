$PROJECT = 'pydatarecognition'
$ACTIVITIES = [
    'version_bump',
    #'changelog',
    'tag',
    'push_tag',
    'ghrelease',
]

# version_bump activity
$VERSION_BUMP_PATTERNS = [
    ('pydatarecognition/__init__.py', r'__version__\s*=.*', "__version__ = '$VERSION'"),
    ('setup.py', r'version\s*=.*,', "version='$VERSION',")
]

# changelog activity
$CHANGELOG_FILENAME = 'CHANGELOG.rst'
$CHANGELOG_IGNORE = ['TEMPLATE.rst']

# tag, push_tag activity
$PUSH_TAG_REMOTE = 'git@github.com:Billingegroup/pydatarecognition.git'

# ghrelease activity
$GITHUB_ORG = 'Billingegroup'
$GITHUB_REPO = 'pydatarecognition'
