# girder-ess-dive

Plugin implementing ESS-DIVE assetstore in Girder

## Install

Copy this directory into girder plugins dir

## Usage

Use Swagger API to use the plugin

### Create a new ESSDIVE Assetstore
```
POST /essdive_assetstores

Params:
name - Name of the Assetstore
url - The base URL for the ESS-DIVE 
```

### Import existing data into an assetstore.
Before you do this you will need to do the following in the Girder Web UI:
- Set the current Girder Assetstore to ESS-DIVE Assetstore
- Create a Collection
- Create a folder to import a dataset into

```
POST /assetstore/{id}/import

Params
id - The Assetstore ID of the ESS-DIVE Assetstore
importPath - the ESS-DIVE dataset ID to import
destinationId - ID of a folder, collection, or user in Girder under which the data will be imported.
destinationType	- Type of the destination resource (Must be set to "Folder).
```

### Downloading data
Browse to your collection. Data should appear there and can be clicked on to download