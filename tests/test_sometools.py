# -*- coding: utf-8 -*-
'''test sometools
Created on Mon 06 Jun 2022 05:56:35 PM PST
Last Modified: Mon 06 Jun 2022 06:15:04 PM PST
'''
from unittest import TestCase

import pandas as pd
import logging
import sometools

LOGGER = logging.getLogger(__name__)

class sometoolsTesting(TestCase):
    def setUp(self) -> None:
        self.st = sometools.tools()

    def tearDown(self):
        self.st = None

    def test_getTushareToken(self):
        token = sometools.getTushareToken()

        LOGGER.info(f"env:{token}")
        self.assertIsNotNone(token, "env must not None")
        self.assertTrue(len(token)> 10, "token length must great then 10.{env}, env type:{type(env)}")


