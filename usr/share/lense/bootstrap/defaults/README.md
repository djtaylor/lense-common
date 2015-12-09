# Lense Bootstrap Answers
The defaults answer file serves as a template for a user-defined answer file. If a user answer file is found, the user file is merged into the template and used by the bootstrap process.

```javascript
{
        "init": {
            "db": {
                "BOOTSTRAP_DB_PASS": "db_passwd"
            }
        },
        "engine": {
            "db_user_password": "db_usr_passwd",
            "db_root_password": "db_root_passwd",
            "api_admin_password": "api_admin_passwd",
            "api_admin_email": "youremail@whatever.com",
            "api_service_email": "youremail@whatever.com",
            "api_service_password": "srvc_acct_passwd",
        },
        "portal": {
            "db_user_password": "db_usr_passwd",
        }
}
```

To use the answers file:

```sh
$ sudo lense-bootstrap -a my_answers.json
```