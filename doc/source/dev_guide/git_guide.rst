.. _git-guide:

This is going to start with the assumption that you have git installed
on your system and you have forked `pyLight` on github.


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

-----
Linux
-----


The global behavior of `git` in controlled through `~/.gitconfig`, which can edited either
directly, or through the command line (`git config ...`).  You can also set repository specific
settings via `repo_path/.gitconfig`.  This is as sugested global configuration file::

   [user]
	name = Your Name
	email = user@bnl.gov
   [color]
   	diff = auto
   	status = auto
   	branch = auto
   [push]
   	default = upstream
---------------
Windows and Mac
---------------

TODO

===================
Forking and Cloning
===================

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

=======
Remotes
=======

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

which can be very useful for collaboration.
