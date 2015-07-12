// main program

// libraries first
@@include('../../bower_components/jquery/dist/jquery.min.js')
@@include('../../bower_components/bootstrap/dist/js/bootstrap.min.js')
@@include('../../bower_components/transparency/dist/transparency.min.js')
@@include('../../bower_components/js-sha256/build/sha256.min.js')
@@include('../../bower_components/marked/marked.min.js')
@@include('../../bower_components/draggabilly/dist/draggabilly.pkgd.min.js')
@@include('../../bower_components/bootbox/bootbox.js')
@@include('../../bower_components/konami-js/konami.js')
@@include('./libraries/prism.js')
@@include('./libraries/jquery.popconfirm.js')


// variables
@@include('_variables.js');

// general functions and utilities
@@include('_functions.js')

// config loading and parsing
@@include('_applyConfig.js')

// initialization
@@include('_init.js')

// socket communication setup
@@include('_socketSetup.js')

// authentication and coachmode
@@include('_auth.js')
