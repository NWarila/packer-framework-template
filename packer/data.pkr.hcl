# ============================================================================================ #
# data.pkr.hcl - Data sources for build metadata                                               #
# ============================================================================================ #

# datasource: ok-at-validate (local Git metadata only; no network or cloud API)
data "git-repository" "cwd" {}
