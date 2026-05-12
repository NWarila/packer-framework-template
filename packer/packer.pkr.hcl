# ============================================================================================ #
# packer.pkr.hcl - Packer version constraint and plugin declarations                           #
# ============================================================================================ #

packer {
  required_version = "= 1.15.0"

  required_plugins {
    git = {
      source  = "github.com/ethanmdavidson/git"
      version = "= 0.6.5"
    }
  }
}
