# In Powershell

Set-ExecutionPolicy Unrestricted
Install-Module -Name PowerShellGet -Force -AllowClobber
Install-Module -Name MicrosoftTeams -Force -AllowClobber

# May need PS restart here

Connect-MicrosoftTeams
# Insert Group Id value - you can find it in URL when copying link to a team
# Provide CSV File Path with list of emails in single column
Import-Csv -Path "[CSV File Path]" | foreach{Add-TeamUser -GroupId "[Group Id]" -user $_.email -role "Member"}