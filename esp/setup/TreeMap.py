from esp.watchlists.models import GetNode

def PopulateInitialDataTree():
    for i in TreeMap:
        GetNode(i)
    

TreeMap = (
    'QualSeriesCategory',
    'QualSeriesCategory/Programs',
    'QualSeriesCategory/Prospectives',
    'QualSeriesCategory/Prospectives/Teachers',
    'QualSeriesCategory/Prospectives/Students',
    'QualSeriesCategory/Prospectives/Volunteers',
    'QualSeriesCategory/Classes',
    'QualSeriesCategory/Subprograms',
    'QualSeriesCategory/Administrivia',
    'QualSeriesCategory/Administrivia/Meetings',
    'QualSeriesCategory/Administrivia/OrganizationalProjects',
    'QualSeriesCategory/ESP',
    'QualSeriesCategory/ESP/Committees',
    'QualSeriesCategory/ESP/Committees/Webministry',
    'QualSeriesCategory/ESP/Committees/Membership',
    'QualSeriesCategory/Community',
    'QualSeriesCategory/Community/Grade6',
    'QualSeriesCategory/Community/Grade7',
    'QualSeriesCategory/Community/Grade8',
    'QualSeriesCategory/Community/Grade9',
    'QualSeriesCategory/Community/Grade10',
    'QualSeriesCategory/Community/Grade11',
    'QualSeriesCategory/Community/Grade12',
    'QualSeriesCategory/Community/Prefrosh',
    'QualSeriesCategory/Community/Member',
    'Verb',
    'Verb/MIT',
    'Verb/dbmail',
    'Verb/dbmail/Subscribe',
    'Verb/registrar',
    'Verb/registrar/Deadline',
    'Verb/registrar/Administer',
    )
