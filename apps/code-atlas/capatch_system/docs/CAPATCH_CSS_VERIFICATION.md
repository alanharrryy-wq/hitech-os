# Capatch CSS Verification

Capatch includes builtin `css-sanity` so mutating `.css` and `.module.css` patches have a real syntax floor instead of fake-green bypasses.

Minimum checks:

- file exists through the normal target file resolver;
- CSS comments close correctly;
- braces balance outside comments and strings;
- Capatch / Visual-Surgery START and END markers match;
- git conflict markers are absent;
- NUL bytes are absent;
- obvious HTML/JS residue is rejected.

Surface cartridges can add stronger checks such as browser screenshots, stylelint, visual diffs, or project-specific gates.
