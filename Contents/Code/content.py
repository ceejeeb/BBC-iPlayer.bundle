import config

class Channel(object):
    def __init__(self, title, thumb, channel_id, live_id):
        self.title = title
        self.thumb = thumb
        self.channel_id = channel_id
        self.live_id = live_id
        self.schedule_url = config.BBC_URL + "/iplayer/schedules/%s" % (self.channel_id)

        base = config.BBC_URL
        if not self.channel_id in ['bbcone', 'bbctwo', 'bbcfour']:
            base = "%s/tv" % (base)
        self.url = "%s/%s" % (base, self.channel_id)

    def highlights_url(self):
        return self.url

    def az_url(self):
        return self.url + "/a-z"

    def has_live_broadcasts(self):
        return self.live_id != None
        
    def has_scheduled_programmes(self):
        return self.live_id != None
        
    def live_url(self):
        return config.BBC_URL + "/iplayer/live/%s" % self.channel_id

tv_channels = {
    #                           title                thumb                  channel_id       live_id
    'bbcone':           Channel('BBC One',           'bbcone.png',          'bbcone',        'bbc_one_london'),
    'bbctwo':           Channel('BBC Two',           'bbctwo.png',          'bbctwo',        'bbc_two_england'),
    'bbcthree':         Channel('BBC Three',         'bbcthree.png',        'bbcthree',      'bbc_three'),
    'bbcfour':          Channel('BBC Four',          'bbcfour.png',         'bbcfour',       'bbc_four'),
    'radio1':           Channel('Radio One',         'bbc_radio_one.png',   'radio1',         None),
    'cbbc':             Channel('CBBC',              'cbbc.png',            'cbbc',          'cbbc'),
    'cbeebies':         Channel('CBeebies',          'cbeebies.png',        'cbeebies',      'cbeebies'),
    'bbcnews':          Channel('BBC News Channel',  'bbcnews.png',         'bbcnews',       'bbc_news24'),
    'parliament':       Channel('BBC Parliament',    'parliament.png',      'bbcparliament', 'bbc_parliament'),
    'bbcalba':          Channel('BBC Alba',          'bbcalba.png',         'bbcalba',       'bbc_alba'),
    's4c':              Channel('S4C',               's4c.png',             's4c',           's4cpbs')
}
ordered_tv_channels = [
    'bbcone', 
    'bbctwo', 
    'bbcthree', 
    'bbcfour', 
    'radio1', 
    'cbbc', 
    'cbeebies', 
    'bbcnews', 
    'parliament', 
    'bbcalba', 
    's4c'
    ]

radio_stations = {
    'bbc_radio_one':                    'BBC Radio 1',
    'bbc_1xtra':                        'BBC 1Xtra',
    'bbc_radio_two':                    'BBC Radio 2',
    'bbc_radio_three':                  'BBC Radio 3',
    'bbc_radio_four':                   'BBC Radio 4',
    'bbc_radio_four_extra':             'BBC Radio 4 Extra',
    'bbc_radio_five_live':              'BBC Radio 5 Live',
    'bbc_radio_five_live_sports_extra': 'BBC Radio 5 Live Sports Extra',
    'bbc_6music':                       'BBC 6 Music',
    'bbc_asian_network':                'BBC Asian Network',  
}

ordered_radio_stations = [
    'bbc_radio_one',
    'bbc_1xtra',
    'bbc_radio_two',
    'bbc_radio_three',
    'bbc_radio_four',
    'bbc_radio_four_extra',
    'bbc_radio_five_live',
    'bbc_radio_five_live_sports_extra',
    'bbc_6music',
    'bbc_asian_network'
]
