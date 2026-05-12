# ============================================================================================ #
# builds.pkr.hcl - Reference build definition                                                  #
# ============================================================================================ #

build {
  name    = "reference"
  sources = ["source.null.reference"]

  provisioner "shell-local" {
    inline = [
      "python -c \"import pathlib; pathlib.Path(r'${local.image.artifact_dir}').mkdir(parents=True, exist_ok=True); pathlib.Path(r'${local.image.manifest_dir}').mkdir(parents=True, exist_ok=True)\"",
      "python -c \"import base64, pathlib; pathlib.Path(r'${local.install_output_path}').write_bytes(base64.b64decode('${base64encode(local.rendered_install_template)}'))\"",
      "python -c \"import base64, pathlib; pathlib.Path(r'${local.build_context_output_path}').write_bytes(base64.b64decode('${base64encode(local.build_context_json)}'))\"",
      "python -c \"print('Rendered ${local.image.install_template.output_file} for ${local.image.key}')\"",
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
      }
    )
  }
}
