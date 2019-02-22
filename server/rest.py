
from girder.api.rest import Resource, RestException
from girder.api.rest import loadmodel
from girder.api import access
from girder.api.describe import describeRoute, Description
from girder.models.item import Item
from girder.models.file import File
from girder.models.assetstore import Assetstore
from girder.constants import AssetstoreType, AccessType
from dateutil import parser
from .constants import ESS_DIVE_URL


class EssDiveAssetstore(Resource):
    def __init__(self):
        super(EssDiveAssetstore, self).__init__()
        self.resourceName = 'essdive_assetstores'

        self.route('POST', (), self.create)
        self.route('POST', (':id', 'files'), self.create_file)

    @access.user
    @loadmodel(model='assetstore')
    @describeRoute(
        Description('Create a file in the ESS DIVE assetstore')
        .param('id', 'The the assetstore to create the file in', required=True, paramType='path')
        .param('name', 'The name of the file.')
        .param('itemId', 'The item to attach the file to.')
        .param('size', 'The size of the file.')
        .param('dateUploaded', 'The created at timestamp')
        .param('fileId', 'The ess-dive id for the file in ess-dive.')
        .param('datasetId', 'The dataset id for the file in ess-dive.')
        .param('mimeType', 'The mimeType of the file.', required=False)
        .param('rightsHolder', 'The rightsholder of the file.', required=False)
        .errorResponse()
    )
    def create_file(self, assetstore, params):
        self.requireParams(('name', 'itemId', 'size', 'dateUploaded', 'fileId', 'datasetId'), params)
        name = params['name']
        item_id = params['itemId']
        size = int(params['size'])
        file_id = params['fileId']
        user = self.getCurrentUser()

        mime_type = params.get('mimeType')
        item = Item().load(id=item_id, user=user,
                           level=AccessType.WRITE, exc=True)

        file = File().createFile(
                        name=name, creator=user, item=item, reuseExisting=True,
                        assetstore=assetstore, mimeType=mime_type, size=size)
        file['file_id'] = file_id
        file['imported'] = True
        file['dateUploaded'] = parser.parse(params['dateUploaded'])
        file['dataset_id'] = params['datasetId']
        file['rightsHolder'] = params.get('rightsHolder')
        File().save(file)

        return File().filter(file)

    def _create_assetstore(self, params):
        """Create a new ESS-DIVE assetstore."""

        return Assetstore().save({
            'type': AssetstoreType.ESSDIVE,
            'name': params.get('name'),
            'essdive': {
                'url': params.get('url', ESS_DIVE_URL)
            }
        })


    @access.user
    @describeRoute(
        Description('Create a new ESS-DIVE assetstore.')
        .param('name', 'Name of the Assetstore')
        .param('url', 'The base URL for the ESS-DIVE API', required=False)
    )
    def create(self, params):
        self.requireParams(('name', 'url'), params)
        return self._create_assetstore(params)
