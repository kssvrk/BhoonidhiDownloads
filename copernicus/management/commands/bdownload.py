from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import django
import sys
sys.path.append(r'C:\Users\rkavu\Desktop\projects\source_code\bhoonidhi\bhoonidhi_downloads')
os.environ['DJANGO_SETTINGS_MODULE'] = 'downloads.settings'
django.setup()
from copernicus.models import DownloadProfile,Downloads
from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
import datetime
from multiprocessing import Pool
import time
from loguru import logger

def downloadProduct(data):

    index,directory_path,username,password=data
    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
    download_data=Downloads.objects.filter(product_id=index).update(start_time=datetime.datetime.now(),status='started')
    download_data=Downloads.objects.get(product_id=index)
    # download_data.start_time=datetime.datimetime.now()
    # download_data.status='started'
    # download_data.save()
    logger.info(f'Downloading product with product_id {index} Started')
    try:
        api.download(index,directory_path=directory_path,checksum=True)
        download_data.end_time=datetime.datetime.now()
        download_data.status='finished'
        download_data.save()
    except Exception as e:
        logger.exception(f'Exception occured {e} while downloading product with   product_id {index}')
        download_data.end_time=datetime.datetime.now()
        download_data.status='error'
        download_data.save()
    except AttributeError as e:
        logger.exception(f'Exception occured {e} while downloading product with   product_id {index}')
        download_data.end_time=datetime.datetime.now()
        download_data.status='error'
        download_data.save()
    logger.info(f'Downloading product with product_id {index} Finished')



class Command(BaseCommand):
    help = 'Installs the download profile based on the argument passed'
    sat_name=''
    def add_arguments(self, parser):
        parser.add_argument('satellite_name', help='Satellite name to start downloads')
    def handle(self, *args, **kwargs):

        sat_name=kwargs['satellite_name']
        self.sat_name=sat_name
        logger.info('------------------------------------------------------')
        logger.info(f'BDOWNLOAD COMMAND EXECUTED WITH ARGUMENT {sat_name}')
        logger.info('------------------------------------------------------')

        #------------- Main Server Loop --------------------------------
        while True:
            try:
                dprofiles=self.getDownloadProfiles()
                if(len(dprofiles)==0):
                    logger.info(f"The satellite_name provided did not have any download profiles configured")
                    logger.info(f"Configure a download profile for downloading products")
                for dprofile in dprofiles:
                    dprofile.updated_time=datetime.datetime.now()#Update the time in downloadprofile
                    dprofile.save()
                    if(sat_name=='Sentinel-1'):
                        self.Sen1Download(dprofile)#Execute Sen1Download
                    elif(sat_name=='Sentinel-2'):
                        self.Sen2Download(dprofile)#Execute Sen1Download
            except Exception as e:
                logger.exception(f'Exception occured {e}')
            except AttributeError as e:
                logger.exception(f'Exception occured {e}')
            #give server some rest , else it will eat your rest
            time.sleep(30)
        #----------------------------------------------------------------
    def getDownloadProfiles(self):
        download_profiles = list(DownloadProfile.objects.filter(satellite_name=self.sat_name,enabled=True))
        return download_profiles
    def checkDownloadExist(self,pid):
        downloads=list(Downloads.objects.filter(product_id=pid))
        if(len(downloads)==0):
            return False
        else:
            return True
    def getPendingDownloads(self,dprofile):
        dprofile.refresh_from_db()#check for dprofile enabled status change to continue or stop downloads
        pending=list(Downloads.objects.filter(satellite_name=self.sat_name,status='queued')|Downloads.objects.filter(satellite_name=self.sat_name,status='error'))
        jobs=[]
        if(dprofile.enabled==True):
            for queue_element in pending:
                pid=queue_element.product_id
                jobs.append([pid,dprofile.download_dir,dprofile.username,dprofile.password])
        return jobs,dprofile
    def DownloadProducts(self,products,dprofile):
        for index in products.keys():
            if(not self.checkDownloadExist(index)):
                download_profile = dprofile
                product_id=index
                title=products[index]['title']
                size=products[index]['size']
                platformname=products[index]['platformname']
                satname=products[index]['title'][0:3]
                queue_time=datetime.datetime.now()
                # end_time=models.DateTimeField(blank=True)
                data_time=products[index]['beginposition']
                product_type=products[index]['producttype']
                status="queued"
                satellite_name=dprofile.satellite_name
                Downloads.objects.create(download_profile=dprofile,product_id=index,title=title,size=size,platformname=platformname,satname=satname,queue_time=queue_time,data_time=data_time,product_type=product_type,status=status,satellite_name=satellite_name)
                logger.info(f'{title} added to queue')
        jobs=self.getPendingDownloads(dprofile)
        p = Pool(concurrency)
        p.map(downloadProduct,jobs)

    def Sen1Download(self,dprofile):
        download_profile_args=[
        dprofile.username,
        dprofile.password,
        dprofile.daysdiff,
        dprofile.shape_file_path,
        dprofile.download_dir,
        dprofile.concurrency,
        ]
        username,password,daysdiff,shape_file,directory_path,concurrency=download_profile_args
        logger.info(f'Sentinel-1 Downloads starting with dprofile = {dprofile}')
        api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
        #shapefileto wkt
        footprint = geojson_to_wkt(read_geojson(shape_file))
        #dates to search
        end_date = datetime.datetime.now()
        daysdiff = datetime.timedelta(days = daysdiff)
        start_date = end_date-daysdiff
        #Search for data
        products = api.query(footprint,
                             date = (start_date,end_date),
                             platformname = 'Sentinel-1',
                             producttype='GRD',
                             )
        self.DownloadProducts(self,products,dprofile)
    def Sen2Download(self,dprofile):
        download_profile_args=[
        dprofile.username,
        dprofile.password,
        dprofile.daysdiff,
        dprofile.shape_file_path,
        dprofile.download_dir,
        dprofile.concurrency,
        ]
        username,password,daysdiff,shape_file,directory_path,concurrency=download_profile_args
        logger.info(f'Sentinel-1 Downloads starting with dprofile = {dprofile}')
        api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')
        #shapefileto wkt
        footprint = geojson_to_wkt(read_geojson(shape_file))
        #dates to search
        end_date = datetime.datetime.now()
        daysdiff = datetime.timedelta(days = daysdiff)
        start_date = end_date-daysdiff
        #Search for data
        products = api.query(footprint,
                             date = (start_date,end_date),
                             platformname = 'Sentinel-2',
                             producttype='S2MSI1C',
                             cloudcoverpercentage = (0, 30)
                             )
        self.DownloadProducts(self,products,dprofile)
