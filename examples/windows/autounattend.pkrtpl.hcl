<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend">
  <settings pass="specialize">
    <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="${architecture}" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
      <ComputerName>${hostname}</ComputerName>
      <TimeZone>${timezone}</TimeZone>
    </component>
  </settings>
  <cpi:offlineImage cpi:source="wim:${os_name}-${os_version}" xmlns:cpi="urn:schemas-microsoft-com:cpi" />
</unattend>
