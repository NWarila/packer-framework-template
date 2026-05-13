selected_image = "reference-windows"

images = {
  reference-linux = {
    os_family    = "linux"
    os_name      = "reference-linux"
    os_version   = "0.1.0"
    architecture = "x86_64"
    tags         = ["reference", "linux", "multi"]

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

  reference-windows = {
    os_family    = "windows"
    os_name      = "windows-server"
    os_version   = "2022"
    architecture = "amd64"
    tags         = ["reference", "windows", "multi"]

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
