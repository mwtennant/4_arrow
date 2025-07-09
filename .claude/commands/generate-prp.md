
# /generate-prp {initial_file}

Read CLAUDE.md, the given initial file and everything in examples/.
Build a Product Requirements Prompt (PRP) in PRPs/ named after the feature slug.

Must include summary, step-by-step plan, file list, validations (pytest & coverage),
and references to examples/docs.

Print the new PRP path when done.
