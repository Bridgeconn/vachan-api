# Vachan Engine V2 - Access Management Process

Vachan Engine V2 contians a set of apis which are refered under multiple categories according to the application. There are endpoints related to Authentication, Contents APis, Project , Translation and dependent apis like Languages, Licenses, versions, content types etc.

## Authentication

Access Restriction is implemented for all the endpoints in different levels based on the apis content priority. User level, Content level, Application level based security is added to each endpoints. Some of the endpoints are open accessible and others are restricted to particualar type of user-roles only. User with specific role permission can only access those apis.Access to endpoints can be done with the help of authorized token.

## How to Access APIs with Token

- open-access apis can be accessed with or without authorization

  ### Access - Restricted Apis via swagger
-   To access restricted APIs user need to have a valid token
- swagger : `https://api.vachanengine.org/docs`
- To authorize all endpoints click the `Authorize button with Lock symbol` on the top of the swagger ui or `Lock symbol` in each api and provide the username(email), password and submit will automatically validate credentials.
- Now the user can access the authorized apis.

### Access - Restricted Apis via HTTP request (eg : curl, REST client like postman)
- Access Api via HTTP request the valid token must provide in the header 'Authorization: Bearer TOKEN_VALUE'
- To get the token, user need to login with valid credentials in the login endpoint.(`v2/user/login`) _if user have no login credentails_ : user need to register first throught the registration endpoint(`v2/user/register`).
- Now the user can use the _token_ get after login, in the request header for authorized access to the api
- Eg: request curl (create source)
```
curl --location --request POST 'https://api.vachanengine.org/v2/sources' \
--header 'Authorization: Bearer TOKEN_VALUE' \
--header 'Content-Type: application/json' \
--data-raw '{
  "contentType": "bible",
  "language": "af",
  "version": "TTT",
  "revision": 1,
  "year": 2022,
  "license": "ISC",
  "accessPermissions": [
    "content"
  ],
  "metaData": {
    "otherName": "Test Source"
  }
}'
```

## Access Rules Configuration

The security implemented for the v2 contents are based on Role Based Access Control(RBAC). RBAC restrict the access based on user's role, access-tags etc.
Structure idea of RBAC in Vachan Engine V2 : 
```
{
    "Entitlement" :{
            "tags" : [role-group]
        }
}
```

Roles describe humans in the identity system (authentication).
Tags are the actions or operations realted to the resource.
Entitlements permitted by (Role, Tag) pairs. The role-tag pair grand the permissions for an action in the request to a particulat resource type.

For better understanding let's walkthrough an example:
```
There are some books need to upload to the server via add-book endpoint and retrieve the books via get-book endpoint. Edit uploaded book via edit-books
so if the following user-roles can perform the actions.

upload :- superuser, admin, content-manager
edit : - superuser , createdUser
read : - NoAuthentication

So the rule json will be something like this

{
    "content":{
        "upload": [superuser, admin, content-manager],
        "edit": [superuser , createdUser],
        "read": [NoAuthentication]
    }
}

for this security create the source with access-permission as CONTENT (ENTITLEMENT)

```

## access_rules.json walkthrough for content management

VachanEngine V2 access rules are described in the [access_rules.json](https://github.com/Bridgeconn/vachan-api/blob/version-2/app/auth/access_rules.json) file  in a configurable format.

VachanEngine V2 deals with different types of contents and all of the contents are connected with source. While creating a `source` the admin must specify the resource type or access-permission-tag for that particular source to ensure the security based on the value of content that is going to be uploaded.

### How to Upload a content

Here we are describing uploading a sample content with access-permissions

- Create a Source for the contents (`v2/sources`)
- specify the access-permissions (one or more) in the accessPermissions list while creating source. Current Accesspermissions according to the access_rule.json are
    - content : allow access  admin level and above (vachanAdmin, superAdmin)
    - open-accees : NoAuthentication
    - publishable : contets that to be publishable
    - downloadable : Contents allowed to download
    - derivable : Content allowed to use for other works like transaltion reference etc.
-   permissions can be edited later for a particular source (`v2/sources`)

- Now all content that going to be uploaded are secured based on the access-tag given while creating the source.

- Now the Content can be uploaded via different apis under this created source

- If no requiered rule set is found in the [access_rules.json](https://github.com/Bridgeconn/vachan-api/blob/version-2/app/auth/access_rules.json)
new rule set can be configured in the json file.

- Eg Rule set in the access_rules.json 
```
"content":{
        "read-via-api":["SuperAdmin", "VachanAdmin", "BcsDeveloper"],
        "read-via-vachanadmin":["SuperAdmin", "VachanAdmin"],
        "create": ["SuperAdmin", "VachanAdmin"],
        "edit": ["SuperAdmin", "resourceCreatedUser"]
    }
here differents permissions are added to the access-permission :- CONTENT like user with which USER-ROLE can read the source via api, vachanAdmin app and which USER-ROLES can create and EDIT the source.
```

### Currently Implemented Access-tags, Pemrissions, User-roles in the [access_rules.json](https://github.com/Bridgeconn/vachan-api/blob/version-2/app/auth/access_rules.json) file related with content management

- content, open-access, publishable, downloadable, derivable, research-use : Resource Type (AccessPermissions of Sources)
- create, edit, process, read, translate etc. permissions 
- User Roles
    - SuperAdmin : Access To All
    - AgAdmin : Autographa Admin
    - VachanAdmin : VachanApp, VachanContent Admin
    - BcsDeveloper : Internal BCS Developer
    - AgUser : Autographa User
    - VachanUser : VachanApp user
    - registeredUser : Api user