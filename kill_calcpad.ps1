Get-Process | Where-Object { $_.ProcessName -like '*Calcpad*' } | Stop-Process -Force
