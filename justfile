target := env('HOME') / '.claude/skills'

# show this help
help:
    @just --list

# link skills into ~/.claude/skills
link:
    mkdir -p {{ target }}
    stow -d {{ justfile_directory() }} -t {{ target }} skills

# unlink
unlink:
    stow -D -d {{ justfile_directory() }} -t {{ target }} skills

# re-link (after adding/removing a skill)
relink:
    mkdir -p {{ target }}
    stow -R -d {{ justfile_directory() }} -t {{ target }} skills
