# ============================================================================================ #
# builds.pkr.hcl - Reference build definition                                                  #
# ============================================================================================ #

build {
  name    = "reference"
  sources = ["source.file.rendered_installer"]

  provisioner "shell-local" {
    env = {
      PACKER_RENDER_REQUEST_B64 = base64encode(local.render_request_json)
    }

    inline = [
      "python \"${path.root}/../tools/render_reference_build.py\"",
    ]
  }

  post-processor "manifest" {
    output     = local.manifest_output_path
    strip_path = true
    strip_time = true
    custom_data = merge(
      local.image.metadata,
      {
        build_version  = data.git-repository.cwd.head
        template_file  = local.image.install_template.output_file
        template_owner = "packer-framework-template"
        secret_seed_id = local.secret_seed_fingerprint
      }
    )
  }
}
