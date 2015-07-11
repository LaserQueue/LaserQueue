// main program

// libraries first
@@include('../../bower_components/jquery/dist/jquery.min.js')
@@include('../../bower_components/bootstrap/dist/js/bootstrap.min.js')
@@include('../../bower_components/transparency/dist/transparency.min.js')
@@include('../../bower_components/fast-sha256/sha256.min.js')
@@include('../../bower_components/marked/marked.min.js')
@@include('../../bower_components/draggabilly/dist/draggabilly.pkgd.min.js')
@@include('../../bower_components/bootbox/bootbox.js')
@@include('konami.js')
@@include('prism.js')
@@include('jquery.popconfirm.js')


// general functions and utilities
@@include('_functions.js')

// config loading and parsing
@@include('_config.js')

// initialization
@@include('_init.js')

// socket communication setup
@@include('_socketSetup.js')

// authentication and coachmode
@@include('_auth.js')
