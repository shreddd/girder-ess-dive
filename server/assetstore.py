#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2015 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import cherrypy
import os
import requests
from dateutil import parser
import xmltodict

from girder.models.model_base import ValidationException, GirderException
from girder.utility.abstract_assetstore_adapter import AbstractAssetstoreAdapter
from girder.api.rest import getCurrentUser
from .constants import ESS_DIVE_URL, ESS_DIVE_QUERY_URL, ESS_DIVE_OBJECT_URL
from .constants import BUF_LEN
from .utils import from_bounds_to_geojson

def get_essdive_metadata(base_url, ess_dive_id):
    object_url = base_url + ESS_DIVE_OBJECT_URL 
    url = "%s/%s" % (object_url, ess_dive_id)
    resp = requests.get(url)
    metadata = xmltodict.parse(resp.content)
    return metadata

def get_essdive_filelist(base_url, ess_dive_id):
    query_url = base_url + ESS_DIVE_QUERY_URL
    # Get the resource map
    fields = "documents,id,resourceMap"
    url = "%s?wt=json&fl=%s&q=id:%s&rows=10000" % (query_url, fields, ess_dive_id)
    resp = requests.get(url)
    json_resp = resp.json()
    resourceMap = json_resp['response']['docs'][0]['resourceMap'][0]
    
    # Get objects in the resource map
    file_fields = "fileName,size,formatType,formatId,id,datasource,rightsHolder,dateUploaded,title,origin"
    files_url = "%s?wt=json&fl=%s&q=resourceMap:%s&rows=10000" % (query_url, file_fields, resourceMap)
    resp = requests.get(files_url)
    json_resp = resp.json()

    return json_resp['response']['docs']
    
class EssDiveAssetstoreAdapter(AbstractAssetstoreAdapter):
    def __init__(self, assetstore):
        self.assetstore = assetstore
        self.url = assetstore['essdive']['url'].rstrip('/')

    @staticmethod
    def validateInfo(doc):
        """
        Ensures we have the necessary information.
        """
        info = doc.get('essdive', {})
        for field in ['url']:
            if field not in info:
                raise ValidationException('Missing %s field.' % field)

        return doc

    def downloadFile(self, file, offset=0, headers=True, endByte=None,
                     **kwargs):

        if 'file_id' not in file:
            raise Exception('Missing ess-dive file_id property')
        object_url = self.url + ESS_DIVE_OBJECT_URL

        url = "%s/%s" % (object_url, file['file_id'])

        if headers:
            raise cherrypy.HTTPRedirect(url)
        else:
            def stream():
                r = requests.get(url, stream=True)
                for chunk in r.iter_content(chunk_size=BUF_LEN):
                    if chunk:
                        yield chunk
            return stream


    def _import_essdive(self, parent, user, ess_dive_id, parent_type='folder'):

        file_objs = get_essdive_filelist(self.url, ess_dive_id)
        metadata = get_essdive_metadata(self.url, ess_dive_id)

        try:
            bbox = metadata['eml:eml']['dataset']['coverage']['geographicCoverage']['boundingCoordinates']
            # convert bbox girder format 
            bounds = from_bounds_to_geojson(
                {
                    'left': float(bbox['westBoundingCoordinate']),
                    'right': float(bbox['eastBoundingCoordinate']),
                    'top': float(bbox['northBoundingCoordinate']),
                    'bottom': float(bbox['southBoundingCoordinate'])
                }, '+init=epsg:4326' # Since it is lat long use WGS84
            )
        except KeyError:
            bounds = None



        for f in file_objs:
            name  = f['fileName']
            size = int(f['size'])
            mimeType = f['formatId']
            item = self.model('item').createItem(
                name=name, creator=user, folder=parent, reuseExisting=True)
            if bounds:
                item['geometa'] = {'bounds': bounds}
                self.model('item').save(item)

            file = self.model('file').createFile(
                name=name, creator=user, item=item, reuseExisting=True,
                assetstore=self.assetstore, mimeType=mimeType, size=size)
            file['imported'] = True
            file['dateUploaded'] = parser.parse(f['dateUploaded'])
            file['file_id'] = f['id']
            file['dataset_id'] = ess_dive_id
            file['rightsHolder'] = f['rightsHolder']

            self.model('file').save(file)

    def importData(self, parent, parentType, params, progress, user, **kwargs):
        ess_dive_id = params.get('importPath', '').strip()

        self._import_essdive(parent, user, ess_dive_id, parent_type=parentType)

    def deleteFile(self, file):
        """
        This assetstore is read-only.
        """
        pass

    def initUpload(self, upload):
        raise NotImplementedError('Read-only, unsupported operation')

    def uploadChunk(self, upload, chunk):
        raise NotImplementedError('Read-only, unsupported operation')

    def finalizeUpload(self, upload, file):
        raise NotImplementedError('Read-only, unsupported operation')

    def cancelUpload(self, upload):
        raise NotImplementedError('Read-only, unsupported operation')

    def requestOffset(self, upload):
        raise NotImplementedError('Read-only, unsupported operation')
