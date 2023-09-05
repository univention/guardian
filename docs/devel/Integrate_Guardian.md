# How to integrate the Guardian with an app

This document aims to provide a walkthrough of the steps necessary to integrate a software with the Guardian.

## Scenario

Let's assume we have a company called "Happy Workplace", that uses a UCS domain for their user management, file shares, etc.

The application "Cake And Kuchen Express" or **CAKE** for short is deployed in this domain as well. This app allows any user
that is logged in, to have a cake or crumpet delivered to a colleague. As you can imagine this service is in high demand
and used often and regularly by employees to surprise each other.

Sadly the HR department of "Happy Workplace" got the message that the usage of **CAKE** strains the budget.
Instead of cancelling the service, HR decided to limit the amount of cake each employee can send per month. Since
"Happy Workplace" utilizes the Guardian for some other services in their domain already, they would like to be able to
use the Guardians roles and rights management to manage the cake quotas as well.

After sending the feature request to the developers of **CAKE** they start their work integrating their application
with the guardian.

## TODO list

1) Add tracking for amount of cakes sent per user per month
2) Make the app and its configuration known to the Guardian
3) Query Guardian for policy decision and interpret result
4) Add or modify roles to add this new permissions to users

The steps one, two and three have to be done by the developers of the **CAKE** application. Step four has to be done by the
administrators of the UCS domain deployed at "Happy Workplace"

### (1) Add tracking for amount of cakes sent per user per month

The Guardian does not add or change data on users, groups or other objects of the domain. It only calculates policies
with data provided to it. Thus, the tracking has to be implemented on the application level. Since **CAKE** is already
integrated with UCS and available in the Univention App Center, the developers decide to add an extended attribute
to the user object in UDM called `cake_counter`. Whenever a user sends a cake via the application the counter is
incremented. They also implement some logic that makes sure to reset the counter at the beginning of each month.

### (2) Make the app and its configuration known to the Guardian

The Guardian itself does not know anything about **CAKE** and its requirements yet. The app has to somehow configure
the Guardian before it can use it. Since **CAKE** is an app in the Univention App Center, the developers decide
to configure the domains' Guardian in the apps join script.

The following steps only illustrate what the developers have to do and are simplified.
In a real scenario they would have to retrieve the domain of the guardian from the UCS domain somehow, for example.
For the sake of this walkthrough we assume the Guardian Management API to be available under the domain `https://management.guardian.intranet`.

The first step is to register the app itself with the Guardian, which gives us the space in which we can add and configure
further objects.

*Currently, the API is not yet authenticated, but once it is this request has to be issued with credentials*
*that grant the right to register apps with the Guardian. This walkthrough will be extended once this is the case.*

```shell
curl -X 'POST' \
  'https://management.guardian.intranet/apps/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "cake",
  "display_name": "Cake And Kuchen Express"
}'

# Response
{
  "app": {
    "name": "cake",
    "display_name": "Cake And Kuchen Express",
    "resource_url": "https://management.guardian.intranet/apps/cake",
    "app_admin": {  # The app_admin field might be subject to change before the first release
      "name": "admin",
      "display_name": "Cake And Kuchen Express Admin",
      "role": {
        "app_name": "cake",
        "namespace_name": "default",
        "name": "admin",
        "display_name": "Cake And Kuchen Express Admin",
        "resource_url": "https://management.guardian.intranet/roles/cake/default/admin"
      }
    }
  }
}
```

This did multiple things at once. It not only created the app `cake` with the guardian, but also the `default` namespace
and the `admin` role, which has administrative rights for everything under the app `cake`.

*Once authentication is added to the Management API all further requests to the management API in this section have to be*
*issued by an authenticated user that has this admin role assigned to it. This walkthrough will be extended once this is the case.*

The next step is creating the permissions that our app needs. The feature request states that *users should only be*
*allowed to send cakes if they did not exceed their monthly limit.* From this we can extract one permission that the
**CAKE** app has to handle from now on: `send_cake`. Let's create it.

```shell
curl -X 'POST' \
  'https://management.guardian.intranet/permissions/cake/default' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "send_cake",
  "display_name": "Sending cakes to colleagues"
}'

#Response
{
  "permission": {
    "app_name": "cake",
    "namespace_name": "default",
    "name": "send_cake",
    "display_name": "Sending cakes to colleagues",
    "resource_url": "https://management.guardian.intranet/permissions/cake/default/send_cake"
  }
}
```

At this point the developers of **CAKE** configured everything necessary to work with the guardian. They could also
create and configure default roles here, that could be used by the administrators of the UCS domain, but since it
was not included in the feature request, they do not do that.

### (3) Query Guardian for policy decision and interpret result

As the last thing the developers of **CAKE** have to do is actually use the Guardian from within their application.
Whenever a user tries to send a cake to a coworker their application queries the Guardian Authorization API. Since
the **CAKE** application does not have access to the complete data of users in the domain, the developers contact the
`with-lookup` version of the `permissions/check` endpoint. This endpoint receives the identifiers of the actor and
targets as well as a list of permissions to check for. It then retrieves the full objects for actor and targets
and returns a result that lists if the actor has the requested permissions when acting on the specified targets.

```shell
# In this specific request the employee Laura M. tries to send a cake to their colleague Francis C.
curl -X 'POST' \
  'https://authz.guardian.intranet/permissions/check/with-lookup' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "actor": {
    "id": "laura.m"
  },
  "targets": [
    {
      "old_target": {
        "id": "francis.c"
      }
    }
  ],
  "permissions_to_check": [
    {
      "app_name": "cake",
      "namespace_name": "default",
      "name": "send_cake"
    }
  ],
  "extra_request_data": {}
}'

#Response
{
  "actor_id": "laura.m",
  "permissions_check_results": [
    {
      "target_id": "francis.c",
      "actor_has_permissions": false
    }
  ],
  "actor_has_all_permissions": false
}
```

The app code has to evaluate the response. In this case we can see that Laura does not have the permission `send_cake`.
Apparently they sent too many cakes already this month! It is the job of the application to interpret the responses from
the Guardian and enforce the results. In this case the UI will show Laura that their request to send a cake was denied.

The Guardian does not enforce policies! It only informs of their results.

With this the job of the developers of **CAKE** is done, and they ship the update via the Univention App Center.

### (4) Add or modify roles to add this new permissions to users

The app update was installed by the administrators of the UCS domain at "Happy Workplace". A couple of days later
they get a report from HR that no one is able to send any cake anymore! They forgot to configure the roles, which means
that no user had the right to send any cakes.

To fix this they have two choices. They can either modify an existing
role to contain the new permission or create a new role just for that. In this situation they decide to go with the second
option and create a new role to allow sending cake with the **CAKE** app.

For the configuration of custom roles they created the app `happy-workplace` after installing the Guardian, and they decide
to reuse this space for the new role. So they do not have to create any new apps or namespaces in the Guardian Management API.

To create the role, they issue the following request:

```shell
curl -X 'POST' \
  'https://management.guardian.intranet/roles/happy-workplace/default' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "cake_sender",
  "display_name": "Cake Sender"
}'

#Response
{
  "role": {
    "app_name": "happy-workplace",
    "namespace_name": "default",
    "name": "cake_sender",
    "display_name": "My Role",
    "resource_url": "https://management.guardian.intranet/roles/happy-workplace/default/cake_sender"
  }
}
```

With that done, they can add the role capability mapping, which assigns permissions to roles:

```shell
curl -X 'PUT' \
  'https://management.guardian.intranet/role_capability_mappings/happy-workplace/default' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "mappings": [
    {
      "role": {
        "app_name": "happy-workplace",
        "namespace_name": "default",
        "name": "cake_sender"
      },
      "conditions": [
        {
          "app_name": "guardian",
          "namespace_name": "default",
          "name": "actor_field_lt",
          "parameters": {
            "field_name": "cake_counter",
            "value": 5
          }
        }
      ],
      "relation": "AND",
      "permissions": [
        {
          "app_name": "cake",
          "namespace_name": "default",
          "name": "send_cake"
        }
      ]
    }
  ]
}'

#Response
{
  "mappings": [
    {
      "role": {
        "app_name": "happy-workplace",
        "namespace_name": "default",
        "name": "cake_sender"
      },
      "conditions": [
        {
          "app_name": "guardian",
          "namespace_name": "default",
          "name": "actor_field_lt",
          "parameters": {
            "field_name": "cake_counter",
            "value": 5
          }
        }
      ],
      "relation": "AND",
      "permissions": [
        {
          "app_name": "cake",
          "namespace_name": "default",
          "name": "send_cake"
        }
      ]
    }
  ]
}
```

Let's dissect this request. We add a new mapping for the role `happy-workplace:default:cake_sender`.
This role gets the permission `cake:default:send_cake`, but only if a condition is fulfilled.
The condition `guardian:default:actor_field_lt` is builtin to the guardian and checks if a field of the actor is
less than a specified value. In this case the parameters are set to the field `cake_counter` and the value it needs
to be less than is set to 5.

Looking back to (3) that means when the app sent the request to the Guardian Authorization API, the extended attribute
of Laura was bigger than 4. Because of that the API answered with `false`. If the value was 4 or less, the API
would have answered with `true` and Laura could have sent another cake.

The final step is to attach the new role to the users in UDM. For that we have to append the full name of the role
to the user object in UDM: `udm users/user modify --dn $DN --append ucsRole=happy-workplace:default:cake_sender`.
It is not possible yet to assign roles on the level of groups, which makes this step rather tedious. But this is
on top of the todo list after the first release of the Guardian.
