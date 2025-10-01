# 🪶 Git Identity Configuration

## 📍 Overview

Every Git commit stores two key pieces of identity metadata:

- **`user.name`** &xrarr; the human-readable name shown as the author and committer.
- **`user.email`** &xrarr; the email address associated with that identity.

These values are resolved at commit time and **baked into the commit object itself** — meaning they determine how your contributions appear in tools like GitHub and how commits are attributed historically.

Git supports configuration at multiple levels:

| Scope  | Applies to                     | Stored in            |
|--------|--------------------------------|----------------------|
| System | All users on the machine       | `/etc/gitconfig`     |
| Global | All repos for the current user | `~/.gitconfig`       |
| Local  | **Only this repository**       | `<repo>/.git/config` |

For project-specific work (e.g., company vs. personal), the **local scope** is the right tool — it overrides global settings and ensures commits in one project use the correct identity.

---

## 🧰 Set project-specific name and email (CLI)

```shell
# Local
git config user.name "ovidiu.pascal"
git config user.email "pascal.ovidiuu@gmail.com"

# To confirm
git config --local --list 
git config --global --list 
```

## 🧪 Changing identity for existing commits (optional)

The above commands affect new commits only. If you need to change the author information on past commits, you must rewrite history (use with care).

>[!INFO]  
> Since I forgot to change my global config and this is a personal project, I needed to switch the pro email associated to my personal one.   
> To do so, i shall be using the [git-filter-repo](https://github.com/newren/git-filter-repo) tool which is **recommended by the git project itself**

>[!WARNING]  
> ⚠️ git filter-repo is a **destructive operation.**
> - It rewrites your entire Git history, changing commit hashes and metadata.
> - It also re-checks out the working directory, which means any unstaged or untracked files WILL BE DELETED.
> - Git cannot recover those files because they were never committed.
> - **Always stash** (git stash -u) or commit your work before running git filter-repo.
> - Best practice: run it on a fresh clone if possible.

```shell
# 1) Install the tool (dont forget to activate the .venv)
uv add --dev git-filter-repo

# 2) Use git filter-repo to (1) update author/committer and (2) rewrite the trailer in messages
git filter-repo --force \
  --commit-callback '
if commit.author_email == b"ovidiu.pascal@orange.com":
    commit.author_email = b"pascal.ovidiuu@gmail.com"
    commit.author_name  = b"ovidiu.pascal"
if commit.committer_email == b"ovidiu.pascal@orange.com":
    commit.committer_email = b"pascal.ovidiuu@gmail.com"
    commit.committer_name  = b"ovidiu.pascal"
' \
  --message-callback '
import re
return re.sub(
    rb"(?mi)^Signed-off-by:\s*ovidiu\.pascal\s*<[^>]+>",
    b"Signed-off-by: ovidiu.pascal <pascal.ovidiuu@gmail.com>",
    message
)
'
# 3) IMPORTANT: filter-repo removes 'origin' to prevent accidental pushes.
#    Re-add your remote and force-push the rewritten history.
git remote add origin git@github.com:Rapture244/ugit_diy.git
# If your default branch is 'main', set upstream the first time you push:
git push --set-upstream --force origin main
# Then push all branches and tags (optional but common after rewrites):
git push --force --all
git push --force --tags




```


