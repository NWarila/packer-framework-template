selected_image = "reference-windows"

images = {
  reference-windows = {
    os_family    = "windows"
    os_name      = "windows-server"
    os_version   = "2022"
    architecture = "amd64"
    tags         = ["reference", "windows", "ci"]

    install_template = {
      template_path = "examples/windows/autounattend.pkrtpl.hcl"
      output_file   = "Autounattend.xml"
      vars = {
        hostname = "ref-win-2022"
        timezone = "UTC"
      }
    }

    metadata = {
      owner        = "platform"
      hardening    = "consumer-owned"
      builder_role = "framework-contract"
    }
  }
}
