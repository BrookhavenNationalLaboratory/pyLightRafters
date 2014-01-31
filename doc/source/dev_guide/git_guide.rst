.. _git-guide:

Introduction to Git
===================

This is going to start with the assumption that you have git (and
gitk) installed on your system and have a `github` account which is a
member of the `BrookhaveNationalLab` organization.




===============
Configuring git
===============

There are many resources on the web for how to use and configure
`git`, this is a streamlined reference for use with `pyLight`.  There
is a variety of gui front ends for `git`, this will demonstrate the
command line usage as the lowest-common-denominator.  On windows and
OSX the `github` applications seems pretty slick and integrates well with
the website.

To make pushing/pulling from `github` as frictionless as possible, it
is best to generate an ssh key pair which will allow see
https://help.github.com/articles/generating-ssh-keys for a through
guide of how to generate and upload the keys to `github`.


The global behavior of `git` in controlled through `~/.gitconfig`
(`C:\Users\MyLogin\.gitconfig` on Windows), which can edited either
directly, or through the command line (`git config --global ...`).
This is as sugested global configuration file::

   [user]
	name = Your Name
	email = user@bnl.gov
   [color]
   	diff = auto
   	status = auto
   	branch = auto
   [push]
   	default = upstream

These settings can be over-ridden on a per-repository basis.


====================
Forking and  Cloning
====================

The first step to with the code in `github` is to create a personal
copy of the repository on `github`.  This is accomplished by
navigating to https://github.com/BrookhavenNationalLaboratory/pyLight
while logged into `github` and click the **fork** button in the upper
right hand corner.  Follow the on-screen and you should now a copy of
the `pyLight` repository attached to your account on `github`.


In order
to work on the code you need to get a copy onto your local machine(s) which is
done via **cloning** your `github` repository to your machine ::

   mkdir ~/my_source  # Any directory will do
   cd ~/my_source     # but this is the scheme I use
   git clone git@github.com:github_user_name/pyLight.git

where `github_user_name` is replaced with your user name.  You may be
asked to unlock your sshkey or authenticate in some way and to accept
the RSA key of the remote host (say yes).  Once you have done this you
should have a folder `pyLight` in your current directory which
contains the most up-to-date version of the code.


========================
Branching and committing
========================

`git` stores the history of code as a series of 'snapshots' of the
project, **commit**\ s, in a tree.  Each **commit** has a unique
identifier generated from it's contents.  A **branch** points to a
single commit and provides a human-readable label for a 'snapshot' in
the project history.

Branching
---------

On a fresh checkout there will be one **branch**, *master*.  To see
a list of the branches currently in your repository run ::

   git branch

which should return ::

   * master

In general, it is a bad idea to work directly on the *master* branch
(for social, not technical reasons), so we will create a new branch to work on ::

   git branch new_feature

To see the results of this run ::
   git branch

again which should now print out ::

   * master
     new_feature

There are two things that are important to note here: first we have
not changed anything about the project, just created a new label for
a commit; second we are still 'on *master* '.  To switch to our new
branch we need to 'check it out' via ::

   git checkout new_feature

Running ::

   git branch

again will confirm that we have switched branches.  We are now ready
to start working.




.. note:: The process of creating and switching to a new branch can be
    done in a single commend with ::

       git checkout -b new_feature


Editing, Staging, Committing
----------------------
Now that we are on a new branch we are ready to start working.  You can
use what ever editor you want to create and edit files.  When you reach a
point in your work when you want to save what you have done (ideally this
should be a minimal self-contained change) it is time to **commit** your
work to git.  The first thing you should do is run ::

  git status

which in the case of working on this text prints ::

    # On branch add_sphinx
    # Changes not staged for commit:
    #   (use "git add <file>..." to update what will be committed)
    #   (use "git checkout -- <file>..." to discard changes in working directory)
    #
    #       modified:   source/dev_guide/git_guide.rst
    #       modified:   source/index.rst
    #
    # Untracked files:
    #   (use "git add <file>..." to include in what will be committed)
    #
    #       source/dev_guide/index.rst
    no changes added to commit (use "git add" and/or "git commit -a")

which shows there are two files that have been changed and one new
file created, and no files added to the **index** sense the last
**commit**.  This message also gives some helpful advice on how to
proceed.  To add files to the commit use **add**  ::

    git add filename1, filename2, ...

You can also use shell expansions.  After running ::

   git add
=============
Collaborating
=============


Remotes
-------

One of the powerful ideas of distributed version control is that all
clones of a repository are *technically* equivolent.  However, for organizational
reasons we desigante one to be the 'canonical' repository, in this case
the repository associated with the `BrookhavenNationalLab` group on github.

In order to get the lastest code from github to your local machine you
need to tell `git` where the other code is.  These locations are, in
the langague of `git`, **remotes**.  The first remote we will want to
add in the canonical repository::

    # make sure you are in the working directory of your local repo
    cd ~/my_source/pyLight
    # add the canonical repo as 'upstream'
    git remote add upstream git@github.com:BrookhavenNationalLaboratory/pyLight.git
    # fetch the commits in the new repository
    git fetch upstream

To checkout your handy work run ::

   git remote -v

which should print something like: ::

    origin  git@github.com:username/pyLight.git (fetch)
    origin  git@github.com:username/pyLight.git (push)
    upstream        git@github.com:BrookhavenNationalLaboratory/pyLight.git (fetch)
    upstream        git@github.com:BrookhavenNationalLaboratory/pyLight.git (push)


which shows two remotes.  It is recommended to re-name `origin` -> `github` ::


   git remote rename origin github

which is the convention that will be used throughout.  You can also add as a remote the
github repositories of other group members, ex ::

   git remote add tacaswell git@github.com:tacaswell/pyLight.git

which will allow you to **fetch** to your local computer any commits they have
**push**\ ed to github.


Fetch
^^^^^

Push
^^^^

Merging
=======

Rebase on to master
===================

