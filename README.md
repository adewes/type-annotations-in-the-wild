# Python Type Annotations in the Wild

This repository contains scripts and notebooks that I used for my Europython
2017 talk in Rimini, where I investigated the usage of type hints in public
Python source code on Github.

## Download the list of repositories

There are two (old-fashioned) Python scripts for downloading a list of Github
repositories via their API. To run them, you need a valid access token that
you can generate in your "Settings" menu. You then put the access token in
the corresponding variable in `settings.py` (or pass it as an environment
variable, which is safer).

`get_top_repositories.py` downloads the top 1000 Python repositories (this is
the maximum number of repositories we can get through this endpoint). Usage:

    python get_top_repositories.py python python_repos.json

Alternatively, you can download the list of ALL Github repositories, though this
will include non-Python repositories (you will have to fetch repository details
later to check the languages, or clone the repo):

    python get_all_repositories.py all_repos.json

After downloading the list of repositories, you can download and analyze the
code by calling `check_for_type_hints.py`:

    python check_for_type_hints.py python_repos.json type_hints.json

This will clone the repositories into a temporary directory
(`/tmp/repos/[github repo name]`), go through each Python file and check for
type hints in it. The script looks for five different types of type hints:

* Function argument annotations (via the AST)
* Return value annoations (via the AST)
* Type comments (via a Regex)
* Imports of the `typing` module (via a Regex)
* `.pyi` files (no further analysis is performed on them)

It then produces for each repository a list of files with the count of each
of the type of information in the list above (except for the `.pyi` files,
where the entry contains only a `true/false` value).

## Notebooks

