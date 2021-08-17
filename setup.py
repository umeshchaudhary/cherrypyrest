"""
    Created on Dec 25 2017
    @author: Umesh Chaudhary
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install sampleproject
    #
    # And where it will live on PyPI: https://pypi.org/project/sampleproject/
    #
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='cherrypyrest',  # Required

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.2.1.9',  # Required

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='A REST like implementation of cherrypy',  # Required

    # This is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    #
    # Often, this is the same as your README, so you can just read it in from
    # that file directly (as we have already done above)
    #
    # This field corresponds to the "Description" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    # long_description=long_description,  # Optional

    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url='https://github.com/umeshchaudhary/cherrypyrest',  # Optional

    # This should be your name or the name of the organization which owns the
    # project.
    author='Umesh Chaudhary',  # Optional

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='2umeshchaudhary@gmail.com',  # Optional

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='cherrypyrest RESTful cherrypy',  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=['cherrypyrest'],  # Required

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'cherrypy',
        'pymongo',
        'bson',
        'pycryptodome',
        'mongomock',
        'pytz'
    ],  # Optional

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    # extras_require={  # Optional
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    # package_data={  # Optional
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    #
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    download_url = 'https://github.com/umeshchaudhary/cherrypyrest/archive/refs/tags/0.2.1.9.zip',
    long_description = '''CherrypyREST
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
'''
)
