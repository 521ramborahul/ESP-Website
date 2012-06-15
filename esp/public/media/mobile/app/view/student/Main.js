Ext.define('LU.view.student.Main', {
    extend: 'Ext.tab.Panel',
    xtype: 'student',
    
    config: {
        tabBarPosition: 'bottom',
        items: [
            {
                xclass: 'LU.view.class.Card'
            },
            {
                title: 'Schedule',
                iconCls: 'time',
                html: 'Schedule Screen'
            }
        ]
    }
});

