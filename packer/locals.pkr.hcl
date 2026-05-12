# ============================================================================================ #
# locals.pkr.hcl - Input normalization and template rendering                                  #
# ============================================================================================ #

locals {
  image_keys        = sort(keys(var.images))
  selected_key      = var.selected_image != "" ? var.selected_image : local.image_keys[0]
  selected_raw      = var.images[local.selected_key]
  selected_metadata = try(local.selected_raw.metadata, {})

  image = {
    key          = local.selected_key
    os_family    = try(local.selected_raw.os_family, "linux")
    os_name      = try(local.selected_raw.os_name, local.selected_key)
    os_version   = try(local.selected_raw.os_version, "0.0.0")
    architecture = try(local.selected_raw.architecture, "x86_64")
    tags         = try(local.selected_raw.tags, [])

    artifact_dir = abspath("${path.root}/${try(local.selected_raw.artifact_dir, "artifacts/${local.selected_key}")}")
    manifest_dir = abspath("${path.root}/${try(local.selected_raw.manifest_dir, "manifests")}")

    install_template = {
      template_path = abspath("${path.root}/${try(local.selected_raw.install_template.template_path, "../examples/linux/cloud-init.pkrtpl.hcl")}")
      output_file   = try(local.selected_raw.install_template.output_file, "user-data")
      vars = merge(
        {
          image_key    = local.selected_key
          os_family    = try(local.selected_raw.os_family, "linux")
          os_name      = try(local.selected_raw.os_name, local.selected_key)
          os_version   = try(local.selected_raw.os_version, "0.0.0")
          architecture = try(local.selected_raw.architecture, "x86_64")
        },
        try(local.selected_raw.install_template.vars, {})
      )
    }

    metadata = merge(
      var.build_context,
      {
        image_key    = local.selected_key
        os_family    = try(local.selected_raw.os_family, "linux")
        os_name      = try(local.selected_raw.os_name, local.selected_key)
        os_version   = try(local.selected_raw.os_version, "0.0.0")
        architecture = try(local.selected_raw.architecture, "x86_64")
      },
      local.selected_metadata
    )
  }

  install_output_path       = "${local.image.artifact_dir}/${local.image.install_template.output_file}"
  build_context_output_path = "${local.image.artifact_dir}/build-context.json"
  manifest_output_path      = "${local.image.manifest_dir}/${local.image.key}.json"

  rendered_install_template = templatefile(
    local.image.install_template.template_path,
    local.image.install_template.vars
  )

  build_context_json = jsonencode(
    merge(
      local.image.metadata,
      {
        git_head      = data.git-repository.cwd.head
        packer_source = "null.reference"
        generated_by  = "packer-framework-template"
      }
    )
  )
}
