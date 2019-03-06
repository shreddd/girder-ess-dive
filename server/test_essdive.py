# Test ESS-DIVE data creation
import unittest
import requests, json

from .assetstore import get_essdive_filelist, get_essdive_metadata


class TestESSDive(unittest.TestCase):
    
    baseurl = "https://data.ess-dive.lbl.gov"


    def test_essdiveid_to_files(self):
        essdiveid = "ess-dive-2f8202e4c0f5ffa-20190215T222733727"
        filelist = get_essdive_filelist(self.baseurl, essdiveid)
        self.assertEqual(len(filelist), 31)

        essdiveid = "ess-dive-d174c363176aaa2-20181206T170812136829"
        filelist = get_essdive_filelist(self.baseurl, essdiveid)
        self.assertEqual(len(filelist), 2)

        essdiveid = "ess-dive-99e9b02216c3a62-20180823T162321432779"
        filelist = get_essdive_filelist(self.baseurl, essdiveid)
        self.assertEqual(len(filelist), 39)

        essdiveid = "ess-dive-ca7ea9922ea9aff-20181219T160938778966"
        filelist = get_essdive_filelist(self.baseurl, essdiveid)
        self.assertEqual(len(filelist), 4)

    def test_get_metadata(self):
        essdiveid = "ess-dive-461f57d68cd162f-20190301T155146455234"
        metadata = get_essdive_metadata(self.baseurl, essdiveid)

        bbox = metadata['eml:eml']['dataset']['coverage']['geographicCoverage']['boundingCoordinates']
        self.assertEqual(bbox['northBoundingCoordinate'], '39.034')

if __name__ == '__main__':
    unittest.main()