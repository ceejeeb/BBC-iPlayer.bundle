import content
import config

TITLE  = "BBC iPlayer CeejeeB"
PREFIX = "/video/iplayer"
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

RE_EPISODE = Regex("Episode ([0-9]+)")
RE_EPISODE_ALT = Regex("Series [0-9]+ *: *([0-9]+)\.")
RE_SERIES = Regex("Series ([0-9]+)")
RE_DURATION = Regex("([0-9]+) *(mins)*")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

RE_FILE = Regex('File1=(https?://.+)')

##########################################################################################
def Start():

    ObjectContainer.title1 = TITLE

    HTTP.CacheTime = CACHE_1MINUTE
    HTTP.Headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0"

##########################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

    oc = ObjectContainer()

    title = "Box Sets"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    BoxSets,
                    title = title,
                    url = config.BBC_URL + '/iplayer/group/p05pn9jr'
                ),
            title = title
        )
    )

    title = "Most Popular"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    MostPopular,
                    title = title,
                    url = config.BBC_URL + '/iplayer/most-popular'
                ),
            title = title
        )
    )

    title = "Live TV"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Live,
                    title = title
                ),
            title = title
        )
    )

    title = "Live Radio"
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    LiveRadio,
                    title = title
                ),
            title = title
        )
    )

    title = "Categories"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Categories,
                    title = title
                ),
            title = title
        )
    )

    title = "A-Z"
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    AToZ,
                    title = title,
                    url = config.BBC_URL + '/iplayer/a-z/'
                ),
            title = title
        )
    )

    channels_oc = TVChannels(title = "TV Channels")
    for object in channels_oc.objects:
        oc.add(object)

    title = "Search"
    oc.add(
        InputDirectoryObject(
            key = 
                Callback(Search),
                title = title, 
                prompt = title
        )
    )

    return oc

##########################################################################################
@route(PREFIX + '/live')
def Live(title):

    oc = ObjectContainer(title2 = title)

    for channel_id in content.ordered_tv_channels:

        channel = content.tv_channels[channel_id]

        if channel.has_live_broadcasts():
            try:
                mdo = URLService.MetadataObjectForURL(channel.live_url())
                mdo.title = channel.title + " - " + mdo.title
                
                oc.add(mdo)
            except:
                pass # Live stream not currently available

    if len(oc) < 1:
        return NoProgrammesFound(oc, title)

    return oc     

##########################################################################################
@route(PREFIX + '/liveradio')
def LiveRadio(title):

    oc = ObjectContainer(title2 = title)

    for station in content.ordered_radio_stations:

        station_img_id = station

        if station in ['bbc_radio_fourfm']:
            station_img_id = 'bbc_radio_four'

        if Client.Product in ['Plex Web', 'Plex for Xbox One'] and not Client.Platform == 'Safari':
            oc.add(
                CreatePlayableObject(
                    title = content.radio_stations[station],
                    thumb = R(station + '.png'),
                    art = config.RADIO_IMG_URL % station_img_id,
                    type = 'mp3',
                    url = config.MP3_URL % station
                )
            )
        else:
            oc.add(
                CreatePlayableObject(
                    title = content.radio_stations[station],
                    thumb = R(station + '.png'),
                    art = config.RADIO_IMG_URL % station_img_id,
                    type = 'hls',
                    url = config.HLS_URL % station
                )
            )                   

    return oc

##########################################################################################
@route(PREFIX + '/tvchannels')
def TVChannels(title):

    oc = ObjectContainer(title2 = title)

    for channel_id in content.ordered_tv_channels:
        channel = content.tv_channels[channel_id]

        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Channel, 
                        channel_id = channel_id
                    ),
                title = channel.title,
                summary = unicode(L(channel_id)),
                thumb = R("%s.png" % channel.thumb)
            )
        )

    return oc

##########################################################################################
@route(PREFIX + "/Channel")
def Channel(channel_id):

    channel = content.tv_channels[channel_id]

    oc = ObjectContainer(title1 = channel.title)

    if channel.has_live_broadcasts():
        try:
            oc.add(URLService.MetadataObjectForURL(channel.live_url()))
        except:
            pass # Live stream not currently available

    title = "Featured"
    oc.add(
        DirectoryObject(
            key =
                Callback(
                    AllEpisodes,
                    title = title,
                    url = channel.highlights_url(),
                    xpath = "//*[@class='gel-layout']//*[contains(@class, 'gel-layout__item')]",
                    page_num = 1,
                    mixed_shows = True
                ),
            title = title,
            thumb = R("%s.png" % channel_id)
        )
    )

    if channel.has_scheduled_programmes():
        # Add the last week's worth of schedules
        now = Datetime.Now()
        for i in range (0, 7):
            date = now - Datetime.Delta(days = i)
            
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            VideosFromSchedule,
                            title = channel.title,
                            url = "%s/%02d%02d%02d" % (channel.schedule_url, date.year, date.month, date.day)
                        ),
                    title = DAYS[date.weekday()],
                    thumb = R("%s.png" % channel_id)
                )
            )

    return oc

##########################################################################################
@route(PREFIX + "/VideosFromSchedule")
def VideosFromSchedule(title, url, channel_id = None):
    return AllEpisodes(title, url, "//*[contains(@class, 'schedule-container')]//*[@class='gel-layout']", 1, True)

##########################################################################################
@route(PREFIX + '/boxsets')
def BoxSets(title, url):
    return AllEpisodes(title, url, "//*[@class='gel-layout']//*[contains(@class, 'gel-layout__item')]", 1, True)

##########################################################################################
@route(PREFIX + '/mostpopular')
def MostPopular(title, url):
    return AllEpisodes(title, url, "//*[@class='gel-layout']//*[contains(@class, 'gel-layout__item')]", 1, True)

##########################################################################################
@route(PREFIX + '/categories')
def Categories(title):
    oc = ObjectContainer(title2 = title)

    pageElement = HTML.ElementFromURL(config.BBC_URL + '/iplayer')

    for item in pageElement.xpath("//*[@class='categories-container']//a[@class='typo typo--canary stat']"): 
        url = item.xpath("./@href")[0]

        if not "/iplayer/categories" in url:
            continue

        if not url.startswith("http"):
            url = config.BBC_URL + url

        title = item.xpath("./text()")[0].strip()

        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        AllEpisodes,
                        title = title,
                        url = url,
                        xpath = "//*[@class='gel-layout']//*[contains(@class, 'gel-layout__item')]",
                        page_num = 1,
                        mixed_shows = True
                    ),
                title = title
            )
        )

    return oc

##########################################################################################
@route(PREFIX + "/atoz")
def AToZ(title, url):
    oc = ObjectContainer(title2 = title)

    for letter in ['0-9'] + list(map(chr, range(ord('a'), ord('z') + 1))):
        oc.add(
            DirectoryObject(
                key =
                    Callback(
                        ProgramsByLetter,
                        url = url,
                        letter = letter.lower()
                    ),
                title = letter.upper()
            )
        )

    return oc

##########################################################################################
@route(PREFIX + "/programsbyletter")
def ProgramsByLetter(url, letter):
    oc = ObjectContainer(title2 = letter.upper())

    pageElement = HTML.ElementFromURL(url + letter)

    for item in pageElement.xpath("//*[contains(@class,'atoz-grid')]//a[contains(@class,'list-content-item')]"):
        url = item.xpath("./@href")[0]

        if not url.startswith("http"):
            url = config.BBC_URL + url

        title = item.xpath(".//*[contains(@class, 'list-content-item__title')]/text()")[0].strip()

        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Episode,
                        title = title,
                        url = url,
                        xpath = "//*[contains(@class, 'grid list__grid')]//*[contains(@class, 'gel-layout__item')]"
                    ),
                title = title
            )
        )

    return oc

##########################################################################################
@route(PREFIX + "/episode")
def Episode(title, url, xpath):
    oc = ObjectContainer(title2 = title)
    pageElement = HTML.ElementFromURL(url)
    allEpisodesUrl = pageElement.xpath(".//*[contains(@class, 'section__header__cta')]/@href")
    if len(allEpisodesUrl) == 1:
        allEpisodesUrl = config.BBC_URL + allEpisodesUrl[0]
    else:
        programmeUrl = pageElement.xpath(".//*[contains(@href, '/programmes')]/@href")[0]
        parts = programmeUrl.split('/')
        if len(parts) == 3:
            allEpisodesUrl = "https://www.bbc.co.uk/iplayer/episodes/" + parts[2]
    

    if allEpisodesUrl:
        return AllEpisodes(title, allEpisodesUrl, "//*[@class='gel-layout']//*[contains(@class, 'grid__item')]")

    return NoProgrammesFound(oc, title)

##########################################################################################
@route(PREFIX + "/Search")
def Search(query):

    url = config.BBC_SEARCH_TV_URL % String.Quote(query)

    return Episodes(
        title = query,
        url = url,
        xpath = "//*[contains(@class,'iplayer-list')]//*[contains(@class,'list-item')]",
        page_num = 1
    )

##########################################################################################
@route(PREFIX + '/allepisodes', page_num = int)
def AllEpisodes(title, url, xpath, page_num = None, mixed_shows = False):
    oc = ObjectContainer(title2 = title)
    orgURL = url

    if page_num is None:
        page_num = 1

    if not '?' in url:
        url = url + "?"
    else:
        url = url + "&"

    url = url + "page=%s" % page_num

    pageElement = HTML.ElementFromURL(url)
    items = pageElement.xpath(xpath)
    show = title

    for item in items:
        try:
            link = item.xpath(".//a/@href")[0]

            if not ('/episode/' in link):
                continue

            if not link.startswith('http'):
                link = config.BBC_URL + link
        except:
            continue

        try:
            title = item.xpath(".//a//*[contains(@class, 'content-item__title')]/text()")[0].strip()
            if show and Client.Platform in ["Plex Home Theater", "Konvergo", "iOS", "Android"]:
                title = "%s, %s" % (show, title)
        except:
            title = show

        try:
            thumb = item.xpath(".//*[contains(@class,'image')]//*/@srcset")[0].split(' ')[0]
        except:
            thumb = None

        try:
            summary = item.xpath(".//a//*[contains(@class, 'content-item__description')]/text()")[1].strip()
        except:
            summary = None
            
        if(mixed_shows):
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Episode,
                            title = title,
                            url = link,
                            xpath = "//*[contains(@class, 'grid list__grid')]//*[contains(@class, 'gel-layout__item')]"
                        ),
                    title = title,
                    thumb = Resource.ContentsOfURLWithFallback(thumb)
                )
            )
        else:
            oc.add(
                EpisodeObject(
                    url = link,
                    title = title,
                    show = show,
                    thumb = Resource.ContentsOfURLWithFallback(thumb),
                    summary = summary
                )
            )

    if len(oc) < 1:
        return NoProgrammesFound(oc, title)

        # See if we need a next button.
    if len(pageElement.xpath("//a[contains(@class, 'pagination__direction--next')]")) > 0:            
        oc.add(
            NextPageObject(
                key = 
                    Callback(
                        AllEpisodes,
                        title = oc.title2, 
                        url = orgURL,
                        xpath = xpath,
                        page_num = int(page_num) + 1,
                        mixed_shows = mixed_shows
                    ),
                title = 'More...'
            )
        )
        
    return oc

##########################################################################################
def NoProgrammesFound(oc, title):

    oc.header  = title
    oc.message = "No programmes found."
    return oc

####################################################################################################
@route(PREFIX + '/CreatePlayableObject', include_container = bool) 
def CreatePlayableObject(title, thumb, art, type, url, include_container = False, **kwargs):
    items = []

    if type == 'mp3':
        codec = AudioCodec.MP3
        container = Container.MP3
        bitrate = 128
        key = Callback(PlayMP3, url = url)

    else:
        codec = AudioCodec.AAC
        container = 'mpegts'
        bitrate = 320
        key = HTTPLiveStreamURL(Callback(PlayHLS, url = url))

    streams = [
        AudioStreamObject(
            codec = codec,
            channels = 2
        )
    ]

    items.append(
        MediaObject(
            bitrate = bitrate,
            container = container,
            audio_codec = codec,
            audio_channels = 2,
            parts = [
                PartObject(
                    key = key,
                    streams = streams
                )
            ]
        )
    )

    if type == 'mp3':
        obj = TrackObject(
                key = 
                    Callback(
                        CreatePlayableObject,
                        title = title,
                        thumb = thumb,
                        art = art,
                        type = type,
                        url = url,
                        include_container = True
                    ),
                rating_key = title,
                title = title,
                items = items,
                thumb = thumb,
                art = art
        )

    else:
        if Client.Platform in ['Plex Home Theater', 'Mystery 4']:
            # Some bug in PHT which can't handle TrackObject below
            obj = VideoClipObject(
                    key = 
                        Callback(
                            CreatePlayableObject,
                            title = title,
                            thumb = thumb,
                            type = type,
                            art = art,
                            url = url,
                            include_container = True
                        ),
                    rating_key = title,
                    title = title,
                    items = items,
                    thumb = thumb,
                    art = art
            )
        else:
            obj = TrackObject(
                    key = 
                        Callback(
                            CreatePlayableObject,
                            title = title,
                            thumb = thumb,
                            type = type,
                            art = art,
                            url = url,
                            include_container = True
                        ),
                    rating_key = title,
                    title = title,
                    items = items,
                    thumb = thumb,
                    art = art
            )

    if include_container:
        return ObjectContainer(objects = [obj])
    else:
        return obj

#################################################################################################### 
@route(PREFIX + '/PlayMP3.mp3')
def PlayMP3(url):
    return PlayAudio(url)
 
#################################################################################################### 
@route(PREFIX + '/PlayHLS.m3u8')
@indirect
def PlayHLS(url):
    
    data = JSON.ObjectFromURL(url)

    hls_url = data['media'][0]['connection'][0]['href']

    return IndirectResponse(
        VideoClipObject,
        key = HTTPLiveStreamURL(url = hls_url)
    )

#################################################################################################### 
def PlayAudio(url):

    content  = HTTP.Request(url).content
    file_url = RE_FILE.search(content)

    if file_url:
        stream_url = file_url.group(1)
        if stream_url[-1] == '/':
            stream_url += ';'
        else:
            stream_url += '/;'

        return Redirect(stream_url)
    else:
        raise Ex.MediaNotAvailable
