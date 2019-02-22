# Test ESS-DIVE data creation
import unittest
import requests, json

from .assetstore import get_essdive_filelist


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

if __name__ == '__main__':
    unittest.main()