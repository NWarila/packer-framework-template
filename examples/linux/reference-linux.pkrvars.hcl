selected_image = "reference-linux"

images = {
  reference-linux = {
    os_family    = "linux"
    os_name      = "reference-linux"
    os_version   = "0.1.0"
    architecture = "x86_64"
    tags         = ["reference", "linux", "ci"]

    install_template = {
      template_path = "examples/linux/cloud-init.pkrtpl.hcl"
      output_file   = "user-data"
      vars = {
        hostname = "reference-linux"
        username = "platform"
      }
    }

    metadata = {
      owner        = "platform"
      hardening    = "consumer-owned"
      builder_role = "framework-contract"
    }
  }
}
