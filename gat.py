#!/usr/bin/env python

# Dependencies:
#     pip install browsercookie

import subprocess
import os
from git import git
from state import opt
from console import CommandLineApplication
from console import cls
from jira.ticket import Ticket
from os.path import expanduser

import webbrowser

options_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gat_temp')
tickets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gat_tickets')

temp_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp.html')

reviewers = ['@seanlanghivida']

ios_path = expanduser('~/via_ios')
ios_project_file_name = 'Via.xcworkspace'

git_url = git.get_remote_from_config()
repo_url = git_url[:-4]

options = opt.read_options(options_path)


def next():
    branch = git.get_branch_with_inc(git.get_current_branch(), git.get_branches_by_commit_date(), 1)
    git.swith_to_branch(branch)


def previous():
    branch = git.get_branch_with_inc(git.get_current_branch(), git.get_branches_by_commit_date(), -1)
    git.swith_to_branch(branch)


def go(index=0):
    if cls.is_flag_set('l') and index == 0:
        list()
        go_to_index_from_input()
        return
    branch = git.get_branches_by_commit_date()[int(index)]
    git.swith_to_branch(branch)


def save(index=0):
    options['stored_branch_' + index] = git.get_current_branch()
    opt.write_options(options_path, options)


def toggle():
    current_branch = git.get_current_branch()
    should_stash = cls.is_flag_set('s')
    if should_stash and git.git_has_uncommited_changes():
        branch_stash()
    branch = current_branch
    try:
        if options['stored_branch_0'] == current_branch:
            branch = options['stored_branch_1']
        else:
            branch = options['stored_branch_0']
    except KeyError:
        pass
    git.swith_to_branch(branch)
    if should_stash:
        branch_stash('apply')


# Todo: go to older branch stashes
def branch_stash(arg1=''):
    current_branch = git.get_current_branch()
    branch_stash_post_fix = '_gat_script'
    if arg1 == 'apply':
        try:
            stash_index = git.get_stash_index_named(current_branch + branch_stash_post_fix)
        except ValueError as e:
            print(e)
            return
        git.get_stash_with_index(stash_index)
    else:
        stash_name = current_branch + branch_stash_post_fix
        print('stashing uncommited changes to stash named ' + stash_name)
        out = subprocess.check_output(['git', 'stash', 'save', stash_name])
        print(out)


def list():
    space = '  '
    marker = '* '
    for index, branch in enumerate(git.get_branches_by_commit_date()):
        pre = marker if git.get_current_branch() == branch else space
        print(pre + str(index) + ') ' + branch)
    if cls.is_flag_set('g'):
        go_to_index_from_input()


def go_to_index_from_input():
    index_from_input = input("Enter index: ")
    go(index_from_input)


def _get_pr_message():
    out = git.pr_message()
    tickets = opt.read_options(tickets_path)
    try:
        url = tickets[git.get_current_branch()]
        out = 'Implements ' + url + '\n\n' + out

        reviewer_string = ''
        for reviewer in reviewers:
            if reviewer_string is not '':
                reviewer_string += ', '
            reviewer_string += reviewer

        out += reviewer_string + ' can you take a look?'
    except KeyError:
        ()
    return out


def pr_message():
    out = _get_pr_message()
    print(out)
    if cls.is_flag_set('m'):
        ()
    if cls.is_flag_set('c'):
        os.system("echo '%s' | pbcopy" % out)


def git_ticket(url=None):
    if (cls.is_flag_set('s') or cls.is_flag_set('c') or cls.is_flag_set('b')) and url is not None:
        if cls.is_flag_set('b'):
            create_branch_from_jira_url(url)
        associate_ticket_url_with_branch(url, git.get_current_branch())
        return
    current_branch = git.get_current_branch()
    try:
        url = get_ticket_url_for_branch(current_branch)
    except KeyError:
        print("No ticket associated with branch '" + current_branch + "'")
        return
    if cls.is_flag_set('d'): # Mark ticket as done
        ticket = Ticket(url)
        url = ticket.get_is_complete_request()
    open_url_in_chrome(url)


def create_branch_from_jira_url(url):
    ticket = Ticket(url)
    branch_name = ticket.get_branch_name()
    git.create_branch(branch_name)

    action_request = ticket.get_is_in_progress()
    open_url_in_chrome(action_request)


def associate_ticket_url_with_branch(url, branch):
    tickets = opt.read_options(tickets_path)
    tickets[branch] = url
    opt.write_options(tickets_path, tickets)


def get_ticket_url_for_branch(branch):
    tickets = opt.read_options(tickets_path)
    return tickets[branch]


def open_url_in_chrome(url):
    chrome_path = 'open -a /Applications/Google\ Chrome.app %s'
    webbrowser.get(chrome_path).open(url)


def ios():
    open_ios_project()


def is_ios():
    return os.getcwd() == ios_path


def open_ios_project():
    project_file_path = os.path.join(ios_path, ios_project_file_name)
    subprocess.check_output(['open', project_file_path])


def new(url):
    create_branch_from_jira_url(url)
    associate_ticket_url_with_branch(url, git.get_current_branch())
    if is_ios():
        open_ios_project()


def soft():
    git.reset_soft()
    print(git.status())


def cherry_pick_from_containing(commit, key):
    commits = git.commits_containing(commit, key)
    cherry_pick_command = git.cherry_pick_from(commits)
    print(cherry_pick_command)

def temp(commit, key):
    commits = git.commits_containing(commit, key)
    cherry_pick_command = git.cherry_pick_from(commits)
    print(cherry_pick_command)


def create_pr():
    current_branch = git.get_current_branch()
    on_remote = git.is_branch_on_remote(repo_url, current_branch)
    has_stashed = False
    rebase = cls.is_flag_set('m')
    if not on_remote:
        if rebase:
            print('Rebasing.')
            git.rebase_branch_onto_remote(current_branch, 'master')
        print('Creating ' + current_branch + ' on remote.')
        git.initial_push(current_branch)

        try:
            url = get_ticket_url_for_branch(current_branch)
        except KeyError:
            print('aborting. key error.')
            return

        ticket = Ticket(url)
        action_request = ticket.get_in_code_review_request()
        open_url_in_chrome(action_request)
    else:
        force = cls.is_flag_set('f')
        stash = cls.is_flag_set('s')
        if not stash:
            if git.git_has_uncommited_changes():
                print('Uncommitted changes. Please commit changes or run with stah flag -s.')
                return
        else:
            print('Stashing changes.')
            branch_stash()
            has_stashed = True

        if rebase:
            print('Rebasing.')
            git.rebase_branch_onto_remote(current_branch, 'master')

        if force or rebase:
            print('Force pushing branch ' + current_branch + ' to remote.')
            git.force_push()
        else:
            print('Pushing to remote')
            git.push()

        if has_stashed:
            branch_stash('apply')

    ticket_url = repo_url + '/compare/' + current_branch + '?expand=1'

    existing_ticket_url = git.get_existing_github_pr_link(ticket_url)
    if existing_ticket_url:
        ticket_url = existing_ticket_url
        open_url_in_chrome(existing_ticket_url)
        return

    message = _get_pr_message()
    if message:
        ticket_url = ticket_url + '&pull_request[body]=' + message
    open_url_in_chrome(ticket_url)


app = CommandLineApplication()
app.install(['next', 'n'], next, 'In a list of branches sorted by commit date, go to an older branch.')
app.install(['prev', 'p'], previous, 'In a list of branches sorted by commit date, go to a newer branch.')
app.install(['list', 'ls', 'l'], list, 'A list of branches sorted by commited date.\nAn optional -g flag will result in a prompt to enter an index.')
app.install(['go', 'g'], go, 'Without arguments, goes to the branch most recently commited to. Takes an optional integer as argument to specify a specific branch to go to in the list.\nThe -l flag without an index argument will first show a list of branches and prompt for an index.')
app.install(['save', 's'], save, "Works in connection with 'toggle'. Takes a 0 or 1 as argument to save a branch for toggeling.")
app.install(['toggle', 't'], toggle, "Works in connection with 'save'. Toggles between saved branches.\nAn options '-s' flag will use branch stashes to stash and apply before and after toggeling. Look at 'stash' for information.")
app.install(['stash'], branch_stash, "Introduces the conecpt of a branch stash. 'br stash' stashes the changes to a branch stash. 'br stash apply' applies branch stashes.")
app.install(['message', 'm'], pr_message, "Creates PR message from commit messages. An optional -c flag copys the message to the clipboard.")
app.install(['ticket', 'tct'], git_ticket, 'Opens the associated ticket. Associate a ticket by using the flag -s and passing a url as argument. An optional -b flag will also create a local branch from the ticket. The -d flag marks a ticket as done.')
app.install(['ios'], ios, 'Opens the ios project.')
app.install(['new', 'n'], new, 'Creates a branch from a Jira ticket url. User has to be logged into Jira.')
app.install(['soft'], soft, 'Alias for git reset --soft HEAD^')
app.install(['pr'], create_pr, 'Creates a pr for the branch.')
app.install(['cherry'], cherry_pick_from_containing, 'Creates a cerry-pick list based on the current branch compared to a previous branch for all commits that contain a keyword. First argument: a branch name or hash. Second argument: a keyword.')
app.install(['temp'], temp, 'Work in progress.')

app.install_default(toggle)
try:
    app.run()
except IndexError:
    print("Error")
except ValueError as e:
    print(e)
