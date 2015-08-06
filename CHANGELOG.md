Changelog
=========

%%version%% (unreleased)
------------------------

- Added the changelog. [David Taylor]

- Need to fix case sensitive debian folder. [David Taylor]

- Needed to track the source format file. [David Taylor]

- Updated permissions on some DEBIAN package files. [David Taylor]

- Fixed both config parser and logger. [David Taylor]

- Moved the debian folder. [djtaylor]

- Changed the package structure for Debian/Ubuntu packaging. [djtaylor]

- Refactoring the common libraries with Python3 coding standards. Also
  updated most of the libraries to work with internal code changes.
  [djtaylor]

- Split off code into a common library package. [djtaylor]

- Created a setup file, need to convert entire codebase for Python
  packaging. [djtaylor]

- Beefed up the feedback class to support text blocks, progress bars,
  and input. Modifications to the setup script. [djtaylor]

- Don't try to import pip module before its installed. [djtaylor]

- Tweaking the setup script. [djtaylor]

- Working on a setup script to be run prior to bootstrapping. [djtaylor]

- Reworking the client interface and modules to make it easier to extend
  and customize. [djtaylor]

- Revising the command line client structure. Created new
  exceptions/objects common modules. [djtaylor]

- Forgot to add utilities/ACL key access combinations. [djtaylor]

- Still debugging ACL object libraries. No objects being retrieved.
  [djtaylor]

- Fixed SocketIO server, was using legacy polling methods. Not needed
  with the new version of the Python SocketIO client. Changing request
  structure to use path/method to load utilities. [djtaylor]

- Encountering error when trying to set the default ACL, added new email
  class in APIBase/APIBare. [djtaylor]

- Still trying to fully reconstruct the database. [djtaylor]

- Need to update the bootstrap script to properly set up all ACL objects
  and keys. [djtaylor]

- Bit more code cleanup. [djtaylor]

- Making final changes to the bootstrapping process. [djtaylor]

- Updates to the bootstrap module. [djtaylor]

- Attempting to create the default admin user/group when bootstrapping
  Cloudscape. [djtaylor]

- Make sure database encryption keys are generated upon bootstrap.
  [djtaylor]

- Not sure how the bootstrap library got moved. [djtaylor]

- Renamed an application from 'auth' to gateway in the API engine
  libraries to avoid conflicts with the built-in Django 'auth'
  application. Also attempting to fix exceptions when running 'syncdb'
  on the engine 'manage.py'. Cleaning out unneeded code in portal.
  [djtaylor]

- Changing the installation script, moving Cloudscape to run entirely in
  userspace. [djtaylor]

- Completely stripping down a branch of 'dev' to make an API as a
  Service application. [djtaylor]

- Update README.md. [David Taylor]

- Update README.md. [David Taylor]

- Going through code after a long hiatus. Cleaning up installation
  scripts and need to sort out bootstrapping the database. Also need to
  work on packaging for the Ubuntu PPA. [djtaylor]

- Only use the Python modules contained in the GitHub sources when
  initially deploying the software. [djtaylor]

- Cleaning up broken imports. The install tool is turning out to be
  useful for debugging. [djtaylor]

- Make the installation manager/worker scripts executable by default.
  [djtaylor]

- Updated old references to deprecated term 'endpoints' to 'utilities'
  [djtaylor]

- Updated a path in the installation worker script. [djtaylor]

- Isolate Python installation into two steps with a wrapper shell
  script. [djtaylor]

- Fixed a broken import. [djtaylor]

- Updates to the installer script. [djtaylor]

- Revisions to the Git source installer and manifest file. [djtaylor]

- Working on a more streamlined source installation. [djtaylor]

- Last commit for the day. [djtaylor]

- Overhauling the portal to get rid of endpoint references. [djtaylor]

- Forgot an extra set of return statements. [djtaylor]

- Incorrect attribute name for getattr() call. [djtaylor]

- Forgot to store the command line flag in a class attribute. [djtaylor]

- Make sure to parse the response 'body' key. [djtaylor]

- Fixed some broken error return logic. [djtaylor]

- Update to client manager class. [djtaylor]

- Fixed some bugs in the APILogger class. [djtaylor]

- Cleaning out references to endpoints in favor of utilities. [djtaylor]

- Reference to an obsolete model attribute. [djtaylor]

- Misspelled class reference. [djtaylor]

- Forgot to rename a key from 'name' to 'path' for a utilities
  reference. [djtaylor]

- Fixed incorrect utilities access class reference. [djtaylor]

- Forgot to wrap a method return in the valid() method. [djtaylor]

- Template validation failing. [djtaylor]

- Log any request data for debugging. [djtaylor]

- Only parse the query string into the data attribute if it isn't empty.
  [djtaylor]

- Query data looks to be getting messed up when constructing the request
  object. [djtaylor]

- Moved some methods/classes around. [djtaylor]

- Better error displaying for command line client. [djtaylor]

- Change logging for request object to show attributes. [djtaylor]

- Print the request object for debugging. [djtaylor]

- Only log the constructed request object for now. [djtaylor]

- Some extra logging. [djtaylor]

- If the user is making a POST request, load the request body into the
  'data' attribute. If the user is making a GET request, convert the
  query string into a dictionary and load into the 'data' attribute.
  [djtaylor]

- Need to account for a possible empty request. [djtaylor]

- More verbose error printing and formatting in APIConnect. [djtaylor]

- Forgot to change a reference from 'TOKEN' to 'KEY' when trying to
  retrieve an authorization token for the request headers. [djtaylor]

- Cleaned up the APIConnect client class. [djtaylor]

- Had to update the client modules to reflect the new request attribute
  changes. [djtaylor]

- Forgot to update the 'utilities' model. [djtaylor]

- Removed the utility 'name' column in favor of a single 'path' column.
  [djtaylor]

- Custom headers not being read by either Apache or Django. [djtaylor]

- Debug logging for the initial request. [djtaylor]

- Going to need to do some major debugging. [djtaylor]

- Completely removing the 'action' parameter in favor of explicit URL
  pathing. [djtaylor]

- Update the group model. [djtaylor]

- Still reworking the API base framework. [djtaylor]

- Re-working the request structure. Removing authorization parameters
  from request body to headers, since GET requests technically aren't
  supposed to have bodies. Renaming 'endpoints' to 'utilities', since
  the entire API is technically accessed by a single endpoint.
  [djtaylor]

- Had to do some debugging on the errors module. Need to start working
  on more wide spread implementation. [djtaylor]

- Looks like 'code' is an internal Python module. [djtaylor]

- Fixed some incorrect variable references. [djtaylor]

- Removed an unused method. Typo fix in errors module. [djtaylor]

- Testing a more robust error response system. [djtaylor]

- Fixed logic error that caused attempted retrieval of a dictionary key
  from a possible NoneType object. [djtaylor]

- Disable autocomplete for all forms and inputs. [djtaylor]

- Final tweaks to the user profile window. [djtaylor]

- Add some more information to the user profile window. [djtaylor]

- Forgot to change the profile pointer border values. [djtaylor]

- Profile menu positioning looks good. [djtaylor]

- Layout changes for portal. [djtaylor]

- Changing styles for the profile window. [djtaylor]

- Set table panel height correctly. [djtaylor]

- Fixed a JavaScript typo. [djtaylor]

- Debugging the bootstrap method. [djtaylor]

- Bootstrap not working on some pages. [djtaylor]

- JS modules not being implemented for some reason. [djtaylor]

- Updated styles for line charts. [djtaylor]

- Placeholder for line chart when no data available. [djtaylor]

- Clear all children of line chart SVG elements when re-rendering.
  [djtaylor]

- Render a message if no data available to render a line chart.
  [djtaylor]

- Need to optimize cluster statistics calculation. Need to account for
  no existing hosts and prevent any math exceptions. [djtaylor]

- Misnamed module in portal Django settings. [djtaylor]

- Added a custom template tag to parse Python values into JavaScript
  values. Forget to store the user's groups in the portal base module.
  [djtaylor]

- Need to make sure template data is being set correctly. [djtaylor]

- Fixed a broken key reference. [djtaylor]

- Group all base template variables into the 'BASE' root key. Prevent
  overwriting of this key. Throw an exception if the a controller tries
  to overwrite. [djtaylor]

- Some last tweaks to the login page. [djtaylor]

- Disable the Chrome browser input yellow background. [djtaylor]

- Disable autocompletion for the login form. [djtaylor]

- Modifications to the login page. [djtaylor]

- Modifications to the login page. [djtaylor]

- Forgot to add the 'is_admin' variable to template data. [djtaylor]

- Forget to extract the discovered element when doing a list
  comprehension. Ran into bug trying to access a nested list. [djtaylor]

- Support for multiple LDAP searches almost done. [djtaylor]

- Need to figure out how to split up LDAP query/auth results depending
  on the LDAP configuration group they were pulled from. [djtaylor]

- Forgot to use *search_union instead of plain search_union. [djtaylor]

- Should have been using filter() instead of get() when trying to access
  the values() method of a model object. [djtaylor]

- Only look for filter attributes in include() arguments if the argument
  is actually non-null. [djtaylor]

- Fixed a logic error when assigning possibly empty/missing attribute
  keys. [djtaylor]

- Testing method seperation to avoid Django settings error. [djtaylor]

- Testing support for LDAP search unions. [djtaylor]

- Conditional includes of template files and JavaScript files/methods
  depending on the value of 'is_admin' [djtaylor]

- Add functionality for toggling API key. [djtaylor]

- Add images to show/hide API key button. [djtaylor]

- Add button to show/hide the API key value. [djtaylor]

- Let the user view their API key in their profile. [djtaylor]

- Moved the logout button. [djtaylor]

- Merging options into profile menu. [djtaylor]

- Changes to the base template. [djtaylor]

- Testing updates to navigation. [djtaylor]

- Remove the password from user queries. [djtaylor]

- Debug statements. [djtaylor]

- Use the built-in 'get_user' method. [djtaylor]

- Don't try to extract attributes from a null object. [djtaylor]

- Fixed a bug causing an exception in auth backend class. [djtaylor]

- Added more logging statements to the auth backend. [djtaylor]

- Still debugging authentication. Looks like the login() method is still
  failing. [djtaylor]

- Still debugging authentication. [djtaylor]

- Still not sure why login is failing. Added some logic to prevent LDAP
  users from logging in if the ldap backend is set to database only.
  [djtaylor]

- Still debugging the login() method. [djtaylor]

- Incorrectly invoked logging statement. [djtaylor]

- Debugging user authentication. [djtaylor]

- Cleaner constructing of the login failure screen. Support kwargs
  argument for app controller methods. [djtaylor]

- Removed some references to deleted variables. [djtaylor]

- Looks like LDAP/database mixed authentication is working for now.
  [djtaylor]

- Debugging user attribute mapping. [djtaylor]

- Replace instances of random/string combinations with a single
  reference to an rstring() method defined in cloudscape.common.utils.
  [djtaylor]

- Generate a random password when creating the initial row for an LDAP
  user. [djtaylor]

- Adding some trace logging. [djtaylor]

- Had to render Collection as dictionary when iterating. [djtaylor]

- Create an LDAP user. [djtaylor]

- Need to map LDAP user attributes to database user attributes.
  [djtaylor]

- Fixed a broken inheritance pattern. [djtaylor]

- Changing the inheritance model for LDAP backend. [djtaylor]

- Had to fix a configuration issue for LDAP auth. [djtaylor]

- Settings not being loaded for some reason for LDAPBackend. [djtaylor]

- Switching to string concat instead of format to prevent mapping
  errors. [djtaylor]

- Problems with importing attributes from LDAP module. [djtaylor]

- Tweaks to the portal settings file. [djtaylor]

- Still tweaking the authentication backend for LDAP. [djtaylor]

- Merge database and LDAP authentication into the same class call.
  [djtaylor]

- Few more tweaks. [djtaylor]

- Still debugging the LDAP backend. [djtaylor]

- Still tweaking LDAP authentication. [djtaylor]

- Fixed a typo. [djtaylor]

- Debugging LDAP authentication. [djtaylor]

- Resolved a circular dependency. [djtaylor]

- Modifications to LDAP authentication. [djtaylor]

- Also changed the way groups are retrieved in portal base. [djtaylor]

- Had to update 'request.py' to account for new group retrieval method.
  [djtaylor]

- Finished debugging the customer user query set. [djtaylor]

- Implementing a custom user query set. [djtaylor]

- Changed the way user's are queried. Query by UUID instead of username.
  [djtaylor]

- Removed a few more references to obsolete user attributes. [djtaylor]

- Removed legacy user attributes. [djtaylor]

- Update the ACL gateway to retrieve group membership by user UUID.
  [djtaylor]

- Internal import for circular dependencies. [djtaylor]

- Tweaks to the group model. [djtaylor]

- Tweaks to API key/token retrieval. [djtaylor]

- Custom user manager. [djtaylor]

- Finished database schema migrations. [djtaylor]

- Tweaks to the user model to account for the new custom model. Going to
  have to re-create some foreign key relationships. [djtaylor]

- Missing an import in 'cloudscape.engine.api.app.user.models'
  [djtaylor]

- Few more tweaks to the settings files. [djtaylor]

- Adjusted the 'AUTH_USER_MODEL' setting. [djtaylor]

- Switched to the new user model in both portal and engine settings
  file. [djtaylor]

- Finalizing tweaks to the custom user model. [djtaylor]

- Had to resolve a circular dependency. [djtaylor]

- Still tweaking changes to the base user model. [djtaylor]

- Still refining the custom user model. [djtaylor]

- Converting to a custom user model for greater flexibility. [djtaylor]

- Trying to clean up the toggle between default database authentication
  and LDAP authentication. [djtaylor]

- Added a default server configuration file to fill out any values that
  aren't explicitly overridden in the user configuration file.
  [djtaylor]

- Broken form field name. [djtaylor]

- Some more tweaks to network utilities. [djtaylor]

- Update the IP block creation JavaScript. [djtaylor]

- Removed a field requirement in portal for creating IPv4/IPv6 blocks.
  [djtaylor]

- Bug fix to router edit JS. [djtaylor]

- Update to router update utility. [djtaylor]

- Updates to portal router update form. [djtaylor]

- Updates to create_router form processing. [djtaylor]

- Few more changes to router templates. [djtaylor]

- Updates to the network endpoint utilities module. [djtaylor]

- Tweaks to the network device models. [djtaylor]

- Add support for removing a router interface. [djtaylor]

- Callback for adding a new interface. [djtaylor]

- Tweaks to the router interfaces HTML. [djtaylor]

- Testing interface update. [djtaylor]

- Skeleton utility for updating a router interface. [djtaylor]

- Add edit/save button for each interface. [djtaylor]

- Edit interfaces on the router details page. [djtaylor]

- Toggle extra attributes for router interfaces. Still need to address
  how to update an interface without creating a seperate page.
  [djtaylor]

- Was using the wrong input name value when submitting network router
  interface hwaddr. [djtaylor]

- Working around the annoying default behaviour of turning datetime
  database fields into an object instead of a string. [djtaylor]

- Was using the wrong object type, should have been 'net_router' instead
  of 'router' [djtaylor]

- Applying a custom network router interfaces queryset. [djtaylor]

- Forgot to return creation parameters for router interfaces. [djtaylor]

- Testing interface creation on routers. [djtaylor]

- Added utility code to add a router interface. [djtaylor]

- Testing network range filter. [djtaylor]

- Trying to add support for IP block filtering. [djtaylor]

- Fixed a bug in the network utils module. [djtaylor]

- Sort network IP blocks by network value. [djtaylor]

- Accidentally overwrote the 'datacenter' key with a router UUID value.
  [djtaylor]

- Forgot to add the ip_block_uuid hidden field. [djtaylor]

- Forgot to remove a reference to an old variable. [djtaylor]

- Should be able to create a new IPv4/IPv6 block now. [djtaylor]

- Problem with initializing CSNetworkIPBlocksList. [djtaylor]

- IPv4/IPv6 blocks JavaScript not loading correctly. [djtaylor]

- Implementing wrong JavaScript library for the IP blocks list page.
  [djtaylor]

- Basic functionality for deleting/creating IPv4/IPv6 blocks. [djtaylor]

- Tweaks to the IPv4/IPv6 block creation utility. [djtaylor]

- Filling out the IPblock sections. [djtaylor]

- Portal flow for updating router details should be good now. [djtaylor]

- Now the '_empty' flag should work. Missed one other check. [djtaylor]

- Fixed support for the '_empty' boolean flag in the JSON template
  validator. [djtaylor]

- Forgot to append the router UUID to the 'router.save' API call.
  [djtaylor]

- Adding ability to update router information. [djtaylor]

- Misnamed API call method in network controller. [djtaylor]

- Filling out the JavaScript for the router details page. [djtaylor]

- Updates to the router details template. [djtaylor]

- Fixed a few more broken variable references. [djtaylor]

- Forgot to rename a variable in copied code. [djtaylor]

- Mis-named object. [djtaylor]

- Debugging a missing attribute in APIQuerySet. [djtaylor]

- Debug logging for APIQuerySet. [djtaylor]

- Clear the 'router_uuid' field after deleting a router. [djtaylor]

- Fixed broken form tag. [djtaylor]

- Sort datacenters response by name. [djtaylor]

- Allow the user to explicity disable using cached results. [djtaylor]

- Added loading windows to datacenter.create/delete. [djtaylor]

- Accidentally overrode a callback object. [djtaylor]

- Forgot to add a hidden field for updating the target router UUID.
  [djtaylor]

- Mis-spelled a function call. [djtaylor]

- Cleaning up JavaScript in portal. [djtaylor]

- Remove check for request path in Socket.IO client and server. Let the
  API server return an error if the request path is invalid. [djtaylor]

- Modifications to the network utilities module, adding portal
  functionality to create/delete routers. [djtaylor]

- Trying to resolve QuerySet class imports. [djtaylor]

- Forgot to import a base module. [djtaylor]

- Fixed a broken Django import. [djtaylor]

- Trying to replace DBAuthACLObjects with ACLObjects and class methods.
  [djtaylor]

- Trying to resolve module dependency issues. [djtaylor]

- Accidentally overwrote a class with the wrong file, whoops. [djtaylor]

- Forgot to add '__init__.py' to new folder. Trying out a shared
  APIQuerySet/APIQueryManager class pair. [djtaylor]

- Streamlining the QuerySet/QueryManager instantiation process.
  [djtaylor]

- Removed another conflicting app name. [djtaylor]

- Removed conflicting Django app names. [djtaylor]

- Needed to change TEMPLATE_DIRS to a tuple by adding a trailing comma.
  [djtaylor]

- Still not sure why from_db_value isn't called. [djtaylor]

- Still tweaking JSONField model. [djtaylor]

- More tweaks to the JSONField model. [djtaylor]

- Stilling trying to figure out why JSONField isn't converting back to a
  JSON object. [djtaylor]

- Update to QuerySet models to account for possible null datacenter
  values. [djtaylor]

- Only accept dict/list/str for JSONField value. [djtaylor]

- Updates to the JSONField model. [djtaylor]

- Modifications to the router creation utility. [djtaylor]

- Testing a new JSONField custom model class to simplify saving and
  retrieving JSON metadata and other objects. [djtaylor]

- Allow the 'datacenter' key to be null for both DBNetworkRouters and
  DBNetworkSwitches. [djtaylor]

- Updates to the NetworkPrefix model. [djtaylor]

- Modifications to custom fields. [djtaylor]

- Added two new custom field subclasses: NullForeignKey and
  NullTextField. Updates to the network models. [djtaylor]

- Updates to the network IP block queryset, new portal template.
  [djtaylor]

- Extract datacenter informtion when running the IP blocks queryset.
  [djtaylor]

- Added custom queryset for both IPv4/IPv6 block models. [djtaylor]

- Added some new module methods for the NetworkAPI client module.
  [djtaylor]

- Make the router field optional when creating an IPv4/IPv6 block.
  [djtaylor]

- Subclass the IPv4/IPv6 utilities. [djtaylor]

- Updates to the IPv6 block model. Added skeleton utilities to
  get/create/update/delete IPv4/IPv6 blocks. [djtaylor]

- Skeleton endpoint utilities for adding/removing network router
  interfaces. [djtaylor]

- Adding content and popups to the routers page. [djtaylor]

- Cleaning up the network routers queryset. [djtaylor]

- Changes to the NetworkRouterGet utility, customizations to the network
  router database model queryset. [djtaylor]

- Always return an array if calling the object class with no object ID
  regardless of the size of the results array. [djtaylor]

- Adding some logging to the object class. [djtaylor]

- Forgot to assign the output of 'query_obj.all()' to itself before
  passing off to the values retrieval method. [djtaylor]

- If no filters applied when doing an object query, use the all()
  method. [djtaylor]

- Forgot to rename a copied variable. [djtaylor]

- Forgot to rename the IPv6 blocks controller method. [djtaylor]

- Skeleton controller methods and template for all network sections.
  [djtaylor]

- Incorrect path name in links, and fixed mis-declared class call.
  [djtaylor]

- Too many 'nav_dropdown_inner' wrappers. [djtaylor]

- 'type' should have been set to 'hover' instead of 'button' [djtaylor]

- Forgot to include the network menu template. [djtaylor]

- Images for network navigation. [djtaylor]

- Added basic network interface to the portal. [djtaylor]

- Was setting an empty string when trying to set the 'auth_error' value
  in ACLGateway. [djtaylor]

- Only apply filters in _get_from_model if they aren't empty. [djtaylor]

- Fixed an empty key bug in an API response for the portal when loading
  the datacenters page with no target datacenter. [djtaylor]

- Removed the 'schedule' client module and created the 'network' client
  module. [djtaylor]

- Testing new endpoint utility to create a network router. [djtaylor]

- Added skeleton endpoints for get/create/delete/update for the network
  router objects. [djtaylor]

- Adding network models. Bug fix in the ACL module that was trying to
  enumerate a possible None value. [djtaylor]

- Getting rid of the schedule endpoint for now. [djtaylor]

- Reworking the build script to do both Debian/RHEL builds at the same
  time. Adding a new endpoint to manage networks. [djtaylor]

- Fixed a broken path in the cloudscape-client postinst script.
  [djtaylor]

- Update to the way permissions are set in the postinst scripts.
  [djtaylor]

- Updates to the control files to support all architectures. Bug fixes
  in the deploy helper script. [djtaylor]

- Some changes to the control files for deb packages. Move control files
  into an 'examples' directory to prevent overwriting when doing a git
  clone and rsync. [djtaylor]

- Changed flags in postinst/postrm scripts to look for symbolic links
  instead of standard files. [djtaylor]

- Update the release in the manifest for each component after a
  successfull build. [djtaylor]

- Should have been using 'exit' instead of 'return' in postinst/postrm
  scripts. [djtaylor]

- Build *.deb packages into the 'output' directory. [djtaylor]

- Made the Debian/Ubuntu build script executable. [djtaylor]

- Testing package building for Debian/Ubuntu: cloudscape-common,
  cloudscape-client, cloudscape-agent. [djtaylor]

- Adding 'build' directory to assist in re-packaging. [djtaylor]

- Falling back to a single Socket.IO server. Not sure how to handle
  request/response routing. Bug fixes to portal logic. [djtaylor]

- Cleaned up the authentication view. [djtaylor]

- Added the 'portal' attribute to all subclasses of View. [djtaylor]

- Still tryinging to clean up inheritance for application views.
  [djtaylor]

- Bug fix in the way the AppBase parent class is initialized for
  application views. [djtaylor]

- Testing out multiple inheritance for application views. Changes in the
  way exceptions are displayed. Bug fix to the 'api_call_threaded'
  method. [djtaylor]

- Trying to modify the Socket.IO server to be able to use Redis when
  clustered. Updated the portal application views. Added a multi-
  threaded API request object to speed up page load times. [djtaylor]

- Modifying the way URLs are dispatched, and the way application views
  are loaded. [djtaylor]

- Modifications to the way the URL is retrieved for the Socket.IO proxy
  for the web client. Updates to the 'cloudscape-socket' script. Added
  new 'bind_ip' config directive for the Socket server. [djtaylor]

- Remove old references to '/portal' in JS/CSS/Python files using the
  old URL structure. [djtaylor]

- Remove code that attempted to change ownership of log files, now
  obsolete with new filesytem structure. [djtaylor]

- Updates to the common variables module. Updates to the way the API
  server URL is retrieved in the client connection manager. [djtaylor]

- Moved some Django configuration settings to the 'server.conf' file.
  Will set dynamically with the config module. [djtaylor]

- Updates to the portal and engine Django settings files. [djtaylor]

- Finally got around to creating a repository for the files I have been
  working on over a remote SSH project. Initial commit of all CloudScape
  files. Cleaned out any sensitive data. [djtaylor]

- Initial commit. [David Taylor]


