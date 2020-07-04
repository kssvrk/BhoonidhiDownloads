from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import sys
from copernicus.models import DownloadProfile,Downloads
from loguru import logger




class Command(BaseCommand):
    help = 'Flushes the started downloads as error to restart them'
    sat_name=''
    def add_arguments(self, parser):
        parser.add_argument('satellite_name', help='Satellite name to flush the started downloads')
    def handle(self, *args, **kwargs):

        sat_name=kwargs['satellite_name']
        self.sat_name=sat_name
        logger.info('------------------------------------------------------')
        logger.info(f'FLUSH COMMAND EXECUTED WITH ARGUMENT {sat_name}')
        logger.info('------------------------------------------------------')

        #------------- get started downloads --------------------------------
        started_downloads=list(Downloads.objects.filter(satellite_name=self.sat_name,status='started'))
        for download in started_downloads:
            download.status='error'
            download.save()
            logger.info(f'Changed the status of {download.title} from started to error')
        #---------------------------------------------------------------------
