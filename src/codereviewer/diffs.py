import subprocess

def get_diff():
    subprocess.run(["git", "fetch", "origin"], check=True)
    result = subprocess.run(["git", "diff", "-U35", "origin/main"], check=True, capture_output=True, text=True)
    return result.stdout

def get_diff_stat():
    subprocess.run(["git", "fetch", "origin"], check=True)
    result = subprocess.run(["git", "diff", "origin/main",  "--numstat"], check=True, capture_output=True, text=True)

    files, insertions, deletions = [], 0, 0

    for line in result.stdout.splitlines():
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        ins, dels, file = parts
        files.append(file)
        insertions += int(ins)
        deletions += int(dels)

    return {
        "files": files,
        "insertions": insertions,
        "deletions": deletions,
        "total": insertions + deletions
    }