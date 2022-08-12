# Backing up DB Volumes ( Vacahn , Kratos )

[Offen docker-volume-backup ](https://github.com/offen/docker-volume-backup) is used for the periodical Backing up of database volumes of Vachan App and Kratos.

## Servers

- vachan App Production Server ( Termed as **Production-server**)
- Internal Backup server (Termed as **DODB-BKP**)

## Current Backing Up process

There are 2 backup process implemented. The processes are setup independenly, one working on the backup-volumes created by the other. Servers are communicated via RSA. In current implementation DODB-BKP have access to production-server to sync the backups via RSA.

### Backup - 1

- Periodical backup of docker volumes are created in the Production-server by Offen.
- The offen backup containers are set in the [Production-Deploy](https://github.com/Bridgeconn/vachan-api/blob/version-2/docker/production-deploy.yml) , [Kratos-Database](https://github.com/Bridgeconn/vachan-api/blob/version-2/docker/Kratos_config/database.yml) yml.
- Offen will be responsible for all features related of backingup like timely backup, cleanup old backups etc.
- Offen backup is at the directory **/var/lib/backups** in the production-server
- offen backup and prune frequencies are in the yml files.

### Backup -2

Second process is an internal backing up to DODB-BKP of same backup volumes created by the offen in the production-server

- Backup-2 is basically a syncing of backup directory of production-server to DODB-BKP
- cronjob and rsync features are used for backup-2
- cronjob structure

```
*        *        *        *        *
minute   hour     day      month    WeekDay
```

- rsync format example

```
rsync [options] "source" "Destination"
```

- In the current implementation cronjob is set in the DODB-BKP server and it read and sync the production-server /var/lib/backups every day at a time (eg : 2:00 am).

- syncing cronjob code example

```
0 2 * * * rsync -au --delete "username@IP:/var/lib/backups/" "/var/dodbbkp"
```

- cronjob can be added/modified by the command

```
crontab -e

edit crontab , save and exit
```
