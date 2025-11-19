import subprocess


def run_git(cmd):
    """Run a git command and return stdout, raise on error."""
    try:
        cp = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return cp.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Command {cmd} failed\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}"
        )


def auto_commit_and_push(message: str, branch: str = "bot_agent", remote: str = "origin", files_path: list[str] = ["."]):
    """Commit and push all changes to the given branch safely."""

    # checkout branch (create if missing)
    try:
        run_git(["git", "checkout", branch])
    except RuntimeError:
        run_git(["git", "checkout", "-b", branch])

    # fetch + pull with rebase
    status = run_git(["git", "status", "--porcelain"])
    if not status:
        print("No changes to commit.")
    else:
        run_git(["git", "add", *files_path])
        try:
            run_git(["git", "commit", "-m", message])
        except RuntimeError as e:
            if "nothing to commit" not in str(e).lower():
                raise

    try:
        return run_git(["git", "push", remote, branch])
    except RuntimeError as e:
        if "set upstream" in str(e).lower():
            return run_git(["git", "push", "-u", remote, branch])
        raise


if __name__ == "__main__":
    print(auto_commit_and_push("test commit"))
