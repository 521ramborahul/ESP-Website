Ext.define('LU.controller.Login', {
    extend: 'Ext.app.Controller',

    config: {
        refs: {
            loginForm: 'loginForm',
            main: 'main'
        },
        control: {
            'loginForm passwordfield': {
                action: 'onLogin'
            }
        }
    },

    onLogin: function(textfield) {
        this.getLoginForm().submit({
            url: '/myesp/ajax_login/',
            method: 'POST',
            params: {
                // tells the server that we are logging in using mobile site
                'isMobile': true
            },

            success: function(form, result) {
                var next;
                if (result.isVolunteer === 'true') {
                    next = Ext.widget('volunteer');
                } else if (result.isStudent == 'true') {
                    next = Ext.widget('student');
                } else {
                    // display error message for unknown role
                    Ext.Msg.alert('Unauthorized Role', 'You have to be either a student or volunteer to access the app.');
                    return;
                }
                Ext.Viewport.getActiveItem().destroy();
                Ext.Viewport.setActiveItem(next);
            },

            failure: function(form, result) {
                console.log(result);
                if (result.message) {
                    Ext.Msg.alert('Login Error', result.message);
                } else if (result.statusText) {
                    Ext.Msg.alert('Login Error', 'An error has occurred. (' + result.statusText + ')')
                } else {
                    Ext.Msg.alert('Login Error', 'An unknown error has occurred. You may wish to try logging again later.');
                }
            }
        });
    }
});

