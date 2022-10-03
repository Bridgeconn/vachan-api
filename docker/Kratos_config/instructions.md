# Configure Ory Kratos Instance Locally

## Ory kratos official documentation

[Ory Kratos](https://www.ory.sh/kratos/docs/)

## How to set up Kratos

- configure docker in local system

- Clone Ory kratos git repo

  `git clone https://github.com/ory/kratos.git`

  `cd kratos`

    <!-- ```git checkout v0.7.4-alpha.1``` -->

  `docker-compose -f quickstart.yml -f quickstart-standalone.yml up --build --force-recreate`

- Once the output slows down and logs indicate a healthy system you're ready to roll! A healthy system will show something along the lines of (the order of messages might be reversed)

  ```
  kratos_1 | time="2020-01-20T14:52:13Z" level=info msg="Starting the public httpd on: 0.0.0.0:4433"
  kratos_1 | time="2020-01-20T14:52:13Z" level=info msg="Starting the admin httpd on: 0.0.0.0:4434"
  ```

---

## Set up Kratos for Vachan-api Authentication

- Replace the **_email-password_** folder in the localtion **_Kratos/contrib/quickstart/kratos/email-password_**
  with folder **_Kratos_config/email-password_** provided in the vachan-api repo

- replace the **_quickstart.yml_** of Ory Kratos with **\*quickstart.yml** in **_Kratos_config_**

- If you want to change the port for postgresDB,
  you can change it here
  **_Kratos/contrib/quickstart/kratos/email-password/Kratos.yml_**

```
postgresd:
    image: postgres:9.6
    ports:
      - "Change Here:5432" #"5431:5432"
```

---

## Set up Environmental Variables

Add the following environmental variables

```
VACHAN_KRATOS_ADMIN_URL = http://127.0.0.1:4434/
VACHAN_KRATOS_PUBLIC_URL = http://127.0.0.1:4433/
VACHAN_TEST_MODE = False
VACHAN_SUPER_USERNAME = <email for super user>
VACHAN_SUPER_PASSWORD = <password for super user>
```

---

## Run and test

- Now Run kratos local instace as mentioned above

- If all goes well , check this http://127.0.0.1:4433/health/alive in your browser gives the following

```
{
"status": "ok"
}
```

- Run the Vachan-api and test the endpoints under the tag _Authentication_ at http://127.0.0.1:8000/docs
