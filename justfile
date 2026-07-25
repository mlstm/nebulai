target := env('HOME') / '.claude/skills'

# show this help
help:
    @just --list

# link skills into ~/.claude/skills
link:
    mkdir -p {{ target }}
    stow -d {{ justfile_directory() }} -t {{ target }} skills

# link .agents/skills into .claude/skills for use in this repo
[unix]
setup:
    @command -v claude >/dev/null || { echo "claude code not found on PATH"; exit 1; }
    mkdir -p {{ justfile_directory() }}/.claude
    ln -sfn ../.agents/skills {{ justfile_directory() }}/.claude/skills

# unlink
unlink:
    stow -D -d {{ justfile_directory() }} -t {{ target }} skills

# re-link (after adding/removing a skill)
relink:
    mkdir -p {{ target }}
    stow -R -d {{ justfile_directory() }} -t {{ target }} skills
