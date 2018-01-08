import subprocess
import os
import re
import browsercookie
import urllib2


def get_remote_from_config():
    reg_exp = r'(\[remote "origin"\]\n\turl = )([a-zA-Z\:\/\._0-9]+)'
    config_dir = os.path.join(os.path.sep, os.getcwd(), '.git', 'config')
    with open(config_dir, 'r') as f:
        content = f.read()

    search = re.search(reg_exp, content, flags=re.M)
    if search:
        return search.group(2)
    raise ValueError('Could not get remote repository from config file')


def get_branches_by_commit_date():
    branches_by_commit_date = subprocess.check_output(
        ['git', 'for-each-ref', '--sort=-committerdate', 'refs/heads/']
    ).splitlines()
    return map(lambda line: line[line.rindex('/') + 1:], branches_by_commit_date)


def get_current_branch():
    git_branch_output = subprocess.check_output(['git', 'branch']).splitlines()
    return filter(lambda line: line[0] == '*', git_branch_output)[0][2:]


def get_branch_with_inc(current_branch, branches, inc):
    for index, branch in enumerate(branches):
        if branch == current_branch:
            return branches[index + inc]
    raise ValueError(current_branch + ' not in list of branches')


def swith_to_branch(branch):
    subprocess.check_output(['git', 'checkout', branch])


def git_has_uncommited_changes():
    return subprocess.check_output(['git', 'diff-index', 'HEAD']) != ""


def get_stash_index_named(name):
    stash_string = subprocess.check_output(['git', 'stash', 'list'])
    re_result = re.search('stash@{([0-9]+)}: On [a-zA-Z_\-0-9]+: ' + name, stash_string)
    if not re_result:
        raise ValueError('No stash found for ' + name + '.')
    return int(re_result.group(1))


def get_stash_with_index(index):
    try:
        git_stash_output = subprocess.check_output(
            ['git', 'stash', 'apply', 'stash@{' + str(index) + '}']
        )
    except subprocess.CalledProcessError:
        return
    print(git_stash_output)


def pr_message():
    current_branch = get_current_branch()
    return unicode(subprocess.check_output(
        ['git', 'log', 'master..' + current_branch, '--pretty=- %s%n%b']
    ), "utf-8")


def create_branch(name):
    branch_creation = subprocess.check_output(['git', 'checkout', '-b', name])
    print(branch_creation)


def is_branch_on_remote(repo_url, branch_name):
    output = subprocess.check_output(['git', 'ls-remote', '--heads', repo_url + '.git', branch_name])
    return len(output) > 0


def force_push():
    output = subprocess.check_output(['git', 'push', '-f'])
    print(output)


def initial_push(branch_name):
    output = subprocess.check_output(['git', 'push', '-u', 'origin', branch_name])
    print(output)


def push():
    output = subprocess.check_output(['git', 'push'])
    print(output)


def rebase_branch_onto_remote(to_be_rebased, rebase_branch):
    output = subprocess.check_output(['git', 'checkout', rebase_branch])
    print(output)
    output = subprocess.check_output(['git', 'pull'])
    print(output)
    output = subprocess.check_output(['git', 'checkout', to_be_rebased])
    print(output)
    output = subprocess.check_output(['git', 'rebase', rebase_branch])
    print(output)
    # if ! git diff-index --quiet HEAD -- ; then
    #     echo "Resolve rebase conflicts before continuing."
    #     exit


def reset_soft():
    subprocess.check_output(
        ['git', 'reset', '--soft', 'HEAD^']
    )


def status():
    return subprocess.check_output(
        ['git', 'status']
    )


def get_existing_github_pr_link(url):
    cj = browsercookie.chrome()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    page = opener.open(url).read()

    re_result = re.search('"(\/vidahealth\/via_ios\/pull\/[0-9]+)"', page)
    if not re_result:
        return None
    return 'https://github.com' + re_result.group(1)


def commits_containing(commit, key):
    current_branch = get_current_branch()
    out = unicode(subprocess.check_output(
        ['git', 'log', commit + '..' + current_branch, '--pretty=- <commit><hash>%h</hash><title>%s</title><body>%b</body></commit>']
    ), "utf-8")
    commits = re.findall('<commit>(.+)<\/commit>', out)
    commits_containing_key = []
    for commit in commits:
        hash_string = re.findall('<hash>(.*)<\/hash>', commit)[0]
        title = re.findall('<title>(.*)<\/title>', commit)[0]
        body = re.findall('<body>(.*)<\/body>', commit)[0]
        message = title + ' ' + body

        if key in message:
            commits_containing_key.append(
                {
                    'hash': hash_string,
                    'title': title,
                    'body': body
                }
            )
    return commits_containing_key


def cherry_pick_from(commits):
    out = u''
    for commit in commits:
        out += 'git cherry-pick ' + commit['hash'] + '\n'
    return out
