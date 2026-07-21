# Recommended GitHub repository ruleset

Apply locally after repository creation:

- protect `main`; require pull requests, but do not require a second developer approval;
- dismiss stale approvals when present; Code Owner review is disabled because this is a sole-developer harness;
- require signed commits where compatible with automation;
- require linear history, conversation resolution, and the full required-check set;
- block force pushes and branch deletion;
- require deployments through protected `publication` and `hugging-face` environments;
- restrict release tag creation and immutable release assets;
- enable secret scanning, push protection, Dependabot alerts, dependency review, private vulnerability reporting, and artifact attestations;
- grant workflows read-only permissions by default and elevate at job scope;
- do not expose Healthpoint, OIA, GitHub, or Hugging Face credentials to pull requests from forks.
