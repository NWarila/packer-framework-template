# ============================================================================================ #
# variables.pkr.hcl - Input variable declarations for the reference Packer framework            #
# ============================================================================================ #

# A map keeps the consumer-facing contract close to real image-factory
# repositories while the reference build selects one image for validation.
variable "images" {
  description = "Image definitions keyed by stable image id. The reference framework builds one selected image from this map."
  type = map(object({
    os_family    = string
    os_name      = string
    os_version   = string
    architecture = string
    tags         = list(string)
    install_template = object({
      template_path = string
      output_file   = string
      vars          = map(string)
    })
    metadata = map(string)
  }))

  default = {
    reference-linux = {
      os_family    = "linux"
      os_name      = "reference-linux"
      os_version   = "0.1.0"
      architecture = "x86_64"
      tags         = ["reference", "linux"]

      install_template = {
        template_path = "examples/linux/cloud-init.pkrtpl.hcl"
        output_file   = "user-data"
        vars = {
          hostname = "reference-linux"
          username = "platform"
        }
      }

      metadata = {
        owner   = "platform"
        purpose = "credential-free validation"
      }
    }
  }

  validation {
    condition     = length(keys(var.images)) > 0
    error_message = "Images must contain at least one image definition."
  }

  validation {
    condition = length([
      for key in keys(var.images) : key
      if key != "" && !can(regex("[\"'\\r\\n/\\\\]", key))
    ]) == length(keys(var.images))
    error_message = "Image keys must be non-empty path-safe identifiers without quotes, slashes, or line breaks."
  }

  validation {
    condition = length([
      for image in values(var.images) : image.install_template.output_file
      if image.install_template.output_file != "" &&
      !contains([".", ".."], image.install_template.output_file) &&
      !can(regex("[\"'\\r\\n/\\\\]", image.install_template.output_file))
    ]) == length(values(var.images))
    error_message = "Each install_template.output_file must be a single file name without quotes, slashes, or line breaks."
  }

  validation {
    condition = length([
      for image in values(var.images) : image.install_template.template_path
      if image.install_template.template_path != "" &&
      !can(regex("[\"'\\r\\n]", image.install_template.template_path)) &&
      !can(regex("(^[A-Za-z]:[\\\\/])|(^[\\\\/])|(^|[\\\\/])\\.\\.([\\\\/]|$)", image.install_template.template_path))
    ]) == length(values(var.images))
    error_message = "Each install_template.template_path must be a repo-relative path without quotes, line breaks, absolute prefixes, or '..' segments."
  }

  validation {
    condition = length([
      for image in values(var.images) : image.os_family
      if contains(["linux", "windows"], lower(image.os_family))
    ]) == length(values(var.images))
    error_message = "Each image os_family must be linux or windows."
  }
}

variable "selected_image" {
  description = "Optional image key from var.images. Empty selects the first key in lexical order."
  type        = string
  default     = ""

  validation {
    condition     = !can(regex("[\"'\\r\\n/\\\\]", var.selected_image))
    error_message = "Selected_image must not contain quotes, slashes, or line breaks."
  }

}

variable "artifact_root" {
  description = "Repo-rooted directory under packer/ where rendered installer artifacts are written."
  type        = string
  default     = "artifacts"

  validation {
    condition = (
      var.artifact_root != "" &&
      !can(regex("[\"'\\r\\n]", var.artifact_root)) &&
      !can(regex("(^[A-Za-z]:[\\\\/])|(^[\\\\/])|(^|[\\\\/])\\.\\.([\\\\/]|$)", var.artifact_root))
    )
    error_message = "Artifact_root must be a relative path without quotes, line breaks, absolute prefixes, or '..' segments."
  }
}

variable "manifest_dir" {
  description = "Repo-rooted directory under packer/ where Packer manifest JSON files are written."
  type        = string
  default     = "manifests"

  validation {
    condition = (
      var.manifest_dir != "" &&
      !can(regex("[\"'\\r\\n]", var.manifest_dir)) &&
      !can(regex("(^[A-Za-z]:[\\\\/])|(^[\\\\/])|(^|[\\\\/])\\.\\.([\\\\/]|$)", var.manifest_dir))
    )
    error_message = "Manifest_dir must be a relative path without quotes, line breaks, absolute prefixes, or '..' segments."
  }
}

variable "build_context" {
  description = "Non-secret run metadata merged into the generated manifest."
  type        = map(string)
  default = {
    environment = "reference"
    owner       = "platform"
  }
}

variable "secret_seed" {
  description = "Sensitive placeholder used to demonstrate Packer sensitive-variable handling without requiring real credentials."
  type        = string
  default     = "reference-only"
  sensitive   = true
}
