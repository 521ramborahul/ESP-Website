//<debug>
Ext.Loader.setPath({
    'Ext': 'sdk/src'
});
//</debug>

Ext.application({
    name: 'LU',

    requires: [
        'Ext.MessageBox'
    ],

    models: [
        'Class'
    ],

    stores: [
        'Classes'
    ],

    controllers: [
        'Login',
        'Classes'
    ],

    views: [
        'Main',
        'Panel',

        'login.LoggedOut',

        'class.Card',
        'class.List',

        'student.Main',

        'volunteer.Main'
    ],

    viewport: {
        autoMaximize: true
    },

    /* TODO: add icon and splash screen
    icon: {
        57: 'resources/icons/Icon.png',
        72: 'resources/icons/Icon~ipad.png',
        114: 'resources/icons/Icon@2x.png',
        144: 'resources/icons/Icon~ipad@2x.png'
    },
    
    phoneStartupScreen: 'resources/loading/Homescreen.jpg',
    */
    launch: function() {
        // Destroy the #appLoadingIndicator element
        Ext.fly('appLoadingIndicator').destroy();

        // Initialize the main view
        Ext.Viewport.add(Ext.create('LU.view.Main'));

        // Obtain CSRF token
        Ext.Ajax.request({
            url: '/set_csrf_token',
            success: function(response) {
                // do nothing
            },
            failure: function(response) {
                if (response.timedout) {
                    Ext.Msg.alert('Timeout', "The server timed out :( Try refreshing the page.");
                } else if (response.aborted) {
                    Ext.Msg.alert('Aborted', "Looks like you aborted the request");
                } else {
                    Ext.Msg.alert('Bad', "Something went wrong with your request");
        }
            }
        });
    },

    onUpdated: function() {
        Ext.Msg.confirm(
            "Application Update",
            "This application has just successfully been updated to the latest version. Reload now?",
            function() {
                window.location.reload();
            }
        );
    }
});
