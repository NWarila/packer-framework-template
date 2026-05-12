#cloud-config
hostname: ${hostname}
users:
  - name: ${username}
    groups: [adm, sudo]
    shell: /bin/bash
    lock_passwd: true
package_update: true
write_files:
  - path: /etc/image-build-metadata
    permissions: "0644"
    content: |
      image_key=${image_key}
      os_family=${os_family}
      os_name=${os_name}
      os_version=${os_version}
      architecture=${architecture}
