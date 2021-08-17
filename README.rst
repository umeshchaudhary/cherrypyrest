CherrypyREST
============

A minimal framework inspired by Django
--------------------------------------

Cherrypyrest is a minimal framework that provides all basic ORM
functionalities and more such as Models, Serializers, REST API
Controllers and some basic common utilities.

How to use
----------

::

    from cherrypyrest import models
    from cherrypyrest import fields as base_fields

    class User(models.Model):

        NAME = 'name'
        EMAIL = 'email'
        AGE = 'age'
        
        fields = [NAME, EMAIL, AGE]

        name = base_fields.String(null=True)
        email = base_fields.Email(required=True)
        age = base_fields.Number()

    user = User()
    user.set_value({"name": "abc", "email": "abc@xyz.com"})
    print(user.db_repr())  # db representation of object
    print(user.serialize()) # json serializable form


    class Address(models.Model):

        CITY = 'city'
        STATE = 'state'
        COUNTRY = 'country'
        POSTAL_CODE = 'postal_code'  # internal representation of a field
        USER = 'user'
        alias = {
              POSTAL_CODE: 'pin_code',  # external or api reppresentation of a field
        }
        fields = [CITY, STATE, COUNTRY, POSTAL_CODE, USER]
        
        city = base_fields.String()
        state = base_fields.String()
        country = base_fields.String()
        postal_code = base_fields.Number(required=True)
        user = base_fields.RelatedField(child=User(), required=True)


    address = Address()

    address.set_value({"state": "ABC", "postal_code": 12345, "user": {"email": "abc@xyz.com"}})

    print(address.serialize())
    #{'city': '',
    # 'state': 'ABC',
    # 'country': '',
    # 'pin_code': 12345,   # use of alias 
    # 'user': {'name': None, 'email': 'abc@xyz.com', 'age': None}}

You can add a lot of attributes in the model class such as
``public_fields``, ``read_only_fields`` etc to make model response more
flexible.

The model works best with MongoDB as the ``ObjectID`` field is already
provided in the fields module. Add a properly setup manager class obejct
in the model.

::

    manager = UserManager()

NOTE: Manager object should have a valid database client object to
connect to. You can conect with any database but mongodb works well
without any changes in the code.

Add an attribute in the models class to identify the database fields
``db_fields`` which gets a list of fields that will be fetched from the
database when required. So in our ``Address`` class

::

    db_fields = [USER]

and then

::

    user = User()
    user.set_value({"email": "abc@xyz.com"})
    user.save()
    user_id = user.pk

    address = Address()
    address.set_value({"postal_code": 234325, "user": user_id})  # no call to the database
    print(address.user.pk)
    # $ ObjectId("23487h2i374x2748bbksjedhskf")
    print(address.user.email)  
    # a call will be initiated to the database to fetch the user object by id and will set the whole object to the user attribute of addres object

So a call to db will only happend when we really need the related data.

I created this small package during my work on a project of one of my
previous company. I haven't really paid a lot of attention to the design
patterns and structure but it worked for me at that time. You can update
the code according to your needs.
