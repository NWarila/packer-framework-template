# ============================================================================================ #
# source.pkr.hcl - Credential-free reference source                                            #
# ============================================================================================ #

source "file" "rendered_installer" {
  content = local.rendered_install_template
  target  = local.install_output_path
}
