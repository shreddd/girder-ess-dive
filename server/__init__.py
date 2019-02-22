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

from girder import events
from girder.api.v1.assetstore import Assetstore
from girder.constants import AssetstoreType
from girder.utility.assetstore_utilities import setAssetstoreAdapter

from .assetstore import EssDiveAssetstoreAdapter
from .rest import EssDiveAssetstore


def updateAssetstore(event):
    params = event.info['params']
    assetstore = event.info['assetstore']

    if assetstore['type'] == AssetstoreType.ESSDIVE:
        assetstore['essdive'] = {
            'url': params.get('url', assetstore['essdive']['url'])
        }

def load(info):

    AssetstoreType.ESSDIVE = 'essdive'
    setAssetstoreAdapter(AssetstoreType.ESSDIVE, EssDiveAssetstoreAdapter)
    events.bind('assetstore.update', 'essdive', updateAssetstore)

    info['apiRoot'].essdive_assetstores = EssDiveAssetstore()
