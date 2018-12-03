from django.contrib.auth.models import User
from jsonfield import JSONField
from django.db import models
from nefarious import quality

PERM_CAN_WATCH_IMMEDIATELY_TV = 'can_immediately_watch_tv'
PERM_CAN_WATCH_IMMEDIATELY_MOVIE = 'can_immediately_watch_movie'


class NefariousSettings(models.Model):
    jackett_host = models.CharField(max_length=500, default='localhost')
    jackett_port = models.IntegerField(default=9117)
    jackett_token = models.CharField(max_length=500)
    transmission_host = models.CharField(max_length=500)
    transmission_port = models.IntegerField(default=9091)
    transmission_user = models.CharField(max_length=500)
    transmission_pass = models.CharField(max_length=500)
    transmission_tv_download_dir = models.CharField(max_length=500, default='tv/', help_text='Relative to download path')
    transmission_movie_download_dir = models.CharField(max_length=500, default='movies/', help_text='Relative to download path')
    tmdb_token = models.CharField(max_length=500)
    tmdb_configuration = JSONField(blank=True, null=True)
    tmdb_configuration_date = models.DateTimeField(blank=True, null=True, auto_now=True)
    quality_profile = models.CharField(max_length=500, default=quality.PROFILE_HD_720P_1080P.name, choices=zip(quality.PROFILE_NAMES, quality.PROFILE_NAMES))

    @classmethod
    def singleton(cls):
        if cls.objects.all().count() > 1:
            raise Exception('Should not have multiple settings records')
        return cls.objects.get()


class WatchMediaBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quality_profile_custom = models.CharField(max_length=500, blank=True, choices=zip(quality.PROFILE_NAMES, quality.PROFILE_NAMES))

    class Meta:
        abstract = True


class WatchMovie(WatchMediaBase):
    tmdb_movie_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    poster_image_url = models.CharField(max_length=1000)
    date_added = models.DateTimeField(auto_now_add=True)
    collected = models.BooleanField(default=False)
    collected_date = models.DateTimeField(blank=True, null=True)
    transmission_torrent_id = models.IntegerField(null=True, blank=True)
    transmission_torrent_hash = models.CharField(max_length=100, blank=True)

    class Meta:
        permissions = (
            (PERM_CAN_WATCH_IMMEDIATELY_MOVIE, 'Can immediately start watching movies'),
        )

    def __str__(self):
        return self.name


class WatchTVShow(WatchMediaBase):
    tmdb_show_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    poster_image_url = models.CharField(max_length=1000)

    class Meta:
        permissions = (
            (PERM_CAN_WATCH_IMMEDIATELY_TV, 'Can immediately start watching tv shows'),
        )

    def __str__(self):
        return self.name


class WatchTVEpisode(WatchMediaBase):
    watch_tv_show = models.ForeignKey(WatchTVShow, on_delete=models.CASCADE)
    tmdb_episode_id = models.IntegerField(unique=True)
    season_number = models.IntegerField()
    episode_number = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    collected = models.BooleanField(default=False)
    collected_date = models.DateTimeField(blank=True, null=True)
    transmission_torrent_id = models.IntegerField(null=True, blank=True)
    transmission_torrent_hash = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('watch_tv_show', 'season_number', 'episode_number')

    def __str__(self):
        return '{} {}x{}'.format(self.watch_tv_show, self.season_number, self.episode_number)


class TorrentBlacklist(models.Model):
    hash = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.hash
