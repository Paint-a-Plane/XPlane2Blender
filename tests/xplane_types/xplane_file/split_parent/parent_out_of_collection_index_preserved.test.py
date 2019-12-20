import inspect

from typing import Tuple
import os
import sys

import bpy
from io_xplane2blender import xplane_config
from io_xplane2blender.tests import *

__dirname__ = os.path.dirname(__file__)

def filterLines(line:Tuple[str])->bool:
    return (isinstance(line[0],str)
             and ("ANIM_" in line[0],
                   "TRIS" in line[0]))

class TestParentOutOfCollectionIndexPreserved(XPlaneTestCase):
    def test_new_branch_index_0(self)->None:
        filename = inspect.stack()[0].function

        self.assertRootObjectExportEqualsFixture(
            bpy.data.collections[filename[5:]],
            os.path.join(__dirname__, "fixtures", filename + ".obj"),
            filename,
            filterLines
        )

    def test_new_branch_index_1(self)->None:
        filename = inspect.stack()[0].function

        self.assertRootObjectExportEqualsFixture(
            bpy.data.collections[filename[5:]],
            os.path.join(__dirname__, "fixtures", filename + ".obj"),
            filename,
            filterLines
        )

    def test_new_branch_index_2(self)->None:
        filename = inspect.stack()[0].function

        self.assertRootObjectExportEqualsFixture(
            bpy.data.collections[filename[5:]],
            os.path.join(__dirname__, "fixtures", filename + ".obj"),
            filename,
            filterLines
        )

    def test_new_branch_index_last(self)->None:
        filename = inspect.stack()[0].function

        self.assertRootObjectExportEqualsFixture(
            bpy.data.collections[filename[5:]],
            os.path.join(__dirname__, "fixtures", filename + ".obj"),
            filename,
            filterLines
        )

    def test_1_reuse_of_parent(self)->None:
        filename = inspect.stack()[0].function

        self.assertRootObjectExportEqualsFixture(
            bpy.data.collections[filename[5:]],
            os.path.join(__dirname__, "fixtures", filename + ".obj"),
            filename,
            filterLines
        )

    def test_1_reuse_of_parent_out_of_order(self)->None:
        filename = inspect.stack()[0].function

        self.assertRootObjectExportEqualsFixture(
            bpy.data.collections[filename[5:]],
            os.path.join(__dirname__, "fixtures", filename + ".obj"),
            filename,
            filterLines
        )

    def test_2_reuse_of_parent(self)->None:
        filename = inspect.stack()[0].function

        self.assertRootObjectExportEqualsFixture(
            bpy.data.collections[filename[5:]],
            os.path.join(__dirname__, "fixtures", filename + ".obj"),
            filename,
            filterLines
        )


runTestCases([TestParentOutOfCollectionIndexPreserved])
