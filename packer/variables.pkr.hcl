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
        template_path = "../examples/linux/cloud-init.pkrtpl.hcl"
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
}

variable "selected_image" {
  description = "Optional image key from var.images. Empty selects the first key in lexical order."
  type        = string
  default     = ""
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
