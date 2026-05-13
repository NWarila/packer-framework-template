# ============================================================================================ #
# locals.pkr.hcl - Input normalization and template rendering                                  #
# ============================================================================================ #

locals {
  image_keys        = sort(keys(var.images))
  selected_key      = var.selected_image != "" ? var.selected_image : local.image_keys[0]
  selected_raw      = var.images[local.selected_key]
  selected_metadata = local.selected_raw.metadata
  repo_root         = abspath("${path.root}/..")

  image = {
    key          = local.selected_key
    os_family    = lower(local.selected_raw.os_family)
    os_name      = local.selected_raw.os_name
    os_version   = local.selected_raw.os_version
    architecture = local.selected_raw.architecture
    tags         = local.selected_raw.tags

    artifact_dir = abspath("${path.root}/${var.artifact_root}/${local.selected_key}")
    manifest_dir = abspath("${path.root}/${var.manifest_dir}")

    install_template = {
      template_path = abspath("${local.repo_root}/${local.selected_raw.install_template.template_path}")
      output_file   = local.selected_raw.install_template.output_file
      vars = merge(
        {
          image_key    = local.selected_key
          os_family    = lower(local.selected_raw.os_family)
          os_name      = local.selected_raw.os_name
          os_version   = local.selected_raw.os_version
          architecture = local.selected_raw.architecture
        },
        local.selected_raw.install_template.vars
      )
    }

    metadata = merge(
      var.build_context,
      {
        image_key    = local.selected_key
        os_family    = lower(local.selected_raw.os_family)
        os_name      = local.selected_raw.os_name
        os_version   = local.selected_raw.os_version
        architecture = local.selected_raw.architecture
      },
      local.selected_metadata
    )
  }

  install_output_path       = "${local.image.artifact_dir}/${local.image.install_template.output_file}"
  build_context_output_path = "${local.image.artifact_dir}/build-context.json"
  builder_contract_path     = "${local.image.artifact_dir}/builder-contract.json"
  manifest_output_path      = "${local.image.manifest_dir}/${local.image.key}.json"
  secret_seed_fingerprint   = substr(sha256(var.secret_seed), 0, 16)

  rendered_install_template = templatefile(
    local.image.install_template.template_path,
    local.image.install_template.vars
  )

  build_context_json = jsonencode(
    merge(
      local.image.metadata,
      {
        git_head       = data.git-repository.cwd.head
        packer_source  = "file.rendered_installer"
        generated_by   = "packer-framework-template"
        secret_seed_id = local.secret_seed_fingerprint
      }
    )
  )

  builder_contract_json = jsonencode({
    image_key      = local.image.key
    builder_family = local.image.os_family
    http_directory = local.image.artifact_dir
    cd_files       = [local.install_output_path]
    boot_command = local.image.os_family == "windows" ? [
      "<wait>",
      "Autounattend.xml is exposed through cd_files for ISO builders.",
      ] : [
      "<wait>",
      "autoinstall ds=nocloud-net;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/",
    ]
  })

  render_request_json = jsonencode({
    repo_root = local.repo_root
    image_key = local.image.key
    files = [
      {
        path        = local.build_context_output_path
        content_b64 = base64encode(local.build_context_json)
      },
      {
        path        = local.builder_contract_path
        content_b64 = base64encode(local.builder_contract_json)
      },
    ]
  })
}
