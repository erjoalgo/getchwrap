getchwrap runs an interactive command and, when you type one of the given
characters, presses Enter for you. It removes the extra keystroke from
programs that ask single-letter questions, such as `git add -p`.

With `--pattern`, it only does this after the program's output matches the
pattern, once per match, so the rest of your typing is unaffected.

To install:

`$ pip install getchwrap`

For example, answer `git commit -p`'s "Stage this hunk?" prompts with a single
key:

```
# answers that skip Enter, after a "Stage ...?" or "Discard ...?" prompt
alias __git-commit-getchwrap='VISUAL=vi getchwrap eynqsh?d -p "(Stage|Discard).+[?] " --'
alias gcp='__git-commit-getchwrap git commit -p'
```

getchwrap exits with the wrapped command's exit status, so `gcp && git push`
only pushes after a successful commit.

See `getchwrap -h` for the options.
