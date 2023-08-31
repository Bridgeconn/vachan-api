# Backing up DB Volumes ( Vacahn , Kratos )

Uses [ofelia scheduler](https://hub.docker.com/r/mcuadros/ofelia/).
All settings are done in the docker-compose alone, and no need to do any configurations on the deployed server to enable this.

## Current Backing Up process

Vachan db backups schedule
- Takes a single dump within the vachan-db postgres container every day at 00:00 am, using pg_dump
- Deletes older backups at 00:00 am from /var/lib/backups 
  - Retains only latest 7 of the daily backups
  - Retains only latest 4 of the weekly backups
  - Retains only latest 12 of the montly dumps
- Copies latest dump from DB container to /var/lib/backups at 03:00 am
  - On every day as daily backup
  - On sundays as weekly backup
  - On first day of every month, as mothly backup
  - On first day of each year, as yearly backup
- Logs the success or failure status of copying and deleting to backup.log in logs volume, shared by other logs like webserver, vachan-api etc

Kratos db backup schedule
- Takes a single dump within the kratos-postgresd container every day at 01:00 am, using pg_dump
- Deletes older backups at 01:00 am from /var/lib/backups 
  - Retains only latest 7 of the daily backups
  - Retains only latest 4 of the weekly backups
  - Retains only latest 12 of the montly dumps
- Copies latest dump from DB container to /var/lib/backups at 04:00 am
  - On every day as daily backup
  - On sundays as weekly backup
  - On first day of every month, as mothly backup
  - On first day of each year, as yearly backup
- Logs the success or failure status of copying and deleting to backup.log in logs volume

:warning: This only copies the backups to the folder /val/lib/backups in the same server where app is deployed. Not moving them to a different server.
