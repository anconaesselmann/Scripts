#!/bin/sh

repo="https://github.com/vidahealth/via_ios"
projectDirName="via_ios"
projectFile="Via.xcworkspace"

pr_setup () {
    if [ ! -d ~/prs ]; then
        mkdir ~/prs
        echo "Created '~/prs'"
    fi
    cd ~/prs
    if [ "$2" == "-r" ] && [ -d $1 ]; then
        echo "Removing '~/prs/$1'"
        rm -rf $1
    fi
    if [ ! -d $1 ]; then
        mkdir $1
        echo "Created '~/prs/$1'"
        cd $1
        echo "Cloning branch $1"
        git clone -b $1 --single-branch "$repo.git"
        cd $projectDirName
        echo "Installing gems"
        gem install --user-install bundler
        bundle install --path ~/.gem/
        echo "Installing pods"
        pod install
    else
        cd ~/prs/$1/$projectDirName
        git reset --hard origin/$1
        git pull
    fi
    open ~/prs/$1/$projectDirName/$projectFile
}

create_github_pr () {
    branchName="$(git branch | grep \* | cut -d ' ' -f2)"
    isBranchOnRemote="$(git ls-remote --heads $repo.git $branchName)"
    if [ -z "$isBranchOnRemote" ]; then
        echo "Pushing $branchName to remote"
        git push -u origin $branchName
    else
        if [ "$1" = "-f" ]; then
            echo "force-pushing $branchName"
            git push -f
        elif [ "$1" = "-m" ]; then
            stashed=false
            if ! git diff-index --quiet HEAD -- ; then
                echo "Stashing uncommited changes"
                git stash
                stashed=true
            else
                echo "Not stashing"
            fi
            git checkout master
            git pull
            git checkout $branchName
            git rebase master

            if ! git diff-index --quiet HEAD -- ; then
                echo "Resolve rebase conflicts before continuing."
                exit
            fi

            git push -f

            if $stashed ; then
                echo "Applying stash"
                git stash apply
            fi
        else
            echo "pushing $branchName"
            git push
        fi
    fi

    url="$repo/pull/new/$branchName"
    echo "Creating PR for $branchName"
    open $url
}

if [ -z "$1" ] || [ "$1" == "-f" ] || [ "$1" == "-m" ]; then
    # No arguments where given. If the current git branch doesn not exist on mremote,
    # push it to remote. Open a browser window to create a new PR for the branch
    create_github_pr $1
else
    # Download the pr passed as argument from remote into a temporary directory and install all dependencies.
    # Open the project once that is done. Pass the optional parameter -r to remove temporary files for that branch first.
    pr_setup $1 $2
fi
