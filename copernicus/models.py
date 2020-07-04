# Create your models here.
from django.db import models

# iterable
STATUS_CHOICES =(
    ("started", "Download Started"),
    ("queued", "Download is Yet to start"),
    ("error", "Download stopped because of error"),
    ("finished", "Download is finished"),
)

class DownloadProfile(models.Model):
    username=models.CharField(max_length=200)
    password=models.CharField(max_length=200)
    concurrency=models.IntegerField(default=1)
    download_dir=models.CharField(max_length=1000)
    shape_file_path=models.CharField(max_length=1000) #shapefile_path
    daysdiff=models.IntegerField(default=3)
    enabled=models.BooleanField(default=False)
    satellite_name=models.CharField(max_length=50,default='Sentinel-1')
    updated_time=models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return f'{self.satellite_name} with {self.daysdiff} days enabled {self.enabled} conc {self.concurrency} by {self.username}  '



class Downloads(models.Model):
    download_profile = models.ForeignKey(DownloadProfile, on_delete=models.CASCADE)
    product_id=models.CharField(max_length=200,unique=True)
    title=models.CharField(max_length=200)
    size=models.CharField(max_length=50)
    platformname=models.CharField(max_length=50)
    satname=models.CharField(max_length=50)
    queue_time=models.DateTimeField(auto_now_add=True,null=True)
    start_time=models.DateTimeField(blank=True,null=True)
    end_time=models.DateTimeField(blank=True,null=True)
    data_time=models.DateField()
    product_type=models.CharField(max_length=50)
    satellite_name=models.CharField(max_length=50,default='Sentinel-1')
    status=models.CharField(choices=STATUS_CHOICES,max_length=50)
    def __str__(self):
        return f'{self.title} of {self.data_time} with status {self.status} started_at {self.start_time}  '
