
# add current module to search path
import os
import sys
sys.path.append( os.path.join(os.path.realpath(__file__),"..") )


import unittest2 as unittest
from qd.cae.dyna import *


class TestDynaModule(unittest.TestCase):
    """Tests the dyna module."""

    def test_dyna_d3plot(self):
        """Testing all D3plot functions"""

        d3plot_filepath = "test/d3plot"
        d3plot_modes = ["in","mid","out","max","min","mean"]
        d3plot_vars = ["disp","vel","accel",
                       "stress","strain","plastic_strain",
                       "history 1 shell","history 1 solid"]
        element_result_list = [None,
                               "plastic_strain",
                               lambda elem : elem.get_plastic_strain()[-1]] 
        part_ids = [1]

        ## D3plot loading
        d3plot = D3plot(d3plot_filepath)
        for mode in d3plot_modes: # load every var with every mode
            d3plot = D3plot(d3plot_filepath)
            vars2 = ["%s %s" % (var,mode) for var in d3plot_vars]
            for var in vars2:
                d3plot.read_states(var)
            d3plot = D3plot(d3plot_filepath,read_states=vars2) # all at once
        d3plot = D3plot(d3plot_filepath,read_states=d3plot_vars) # default mode (mode=mean)
        # D3plot functions
        self.assertEqual( d3plot.get_nNodes()        ,4915)
        self.assertEqual( len(d3plot.get_nodes())    ,4915)
        self.assertEqual( d3plot.get_nElements()     ,4696)
        self.assertEqual( d3plot.get_nElements("beam")  ,0)
        self.assertEqual( d3plot.get_nElements("shell") ,4696)
        self.assertEqual( d3plot.get_nElements("solid") ,0)
        self.assertEqual( len(d3plot.get_elements()) ,4696)
        self.assertEqual( d3plot.get_timesteps()[0]  ,0.)
        self.assertEqual( len(d3plot.get_timesteps()) ,1)
        self.assertEqual( len(d3plot.get_parts())     ,1)
        export_path = os.path.join( os.path.dirname(__file__), "test_export.html" )
        for element_result in element_result_list:
            
            # test d3plot.plot directly
            d3plot.plot(iTimestep=-1, element_result=element_result, export_filepath=export_path)
            self.assertTrue( os.path.isfile(export_path) )
            os.remove(export_path)
            
            # test plotting by parts
            D3plot.plot_parts(d3plot.get_parts(), iTimestep=-1, element_result=element_result, export_filepath=export_path)
            self.assertTrue( os.path.isfile(export_path) )
            os.remove(export_path)

            for part in d3plot.get_parts():
                part.plot(iTimestep=-1, element_result=element_result, export_filepath=export_path)
                self.assertTrue( os.path.isfile(export_path) )
                os.remove(export_path)

            for part_id in part_ids:
                d3plot.get_partByID(part_id).plot(iTimestep=-1, element_result=None, export_filepath=export_path)
                self.assertTrue( os.path.isfile(export_path) )
                os.remove(export_path)
        
        ## D3plot error handling
        # ... TODO

        ## Node
        node_ids = [1,2]
        nodes_ids_v1 = [d3plot.get_nodeByID(node_id) for node_id in node_ids]
        nodes_ids_v2 = d3plot.get_nodeByID(node_ids)
        self.assertItemsEqual( [node.get_id() for node in nodes_ids_v1] , node_ids )
        self.assertItemsEqual( [node.get_id() for node in nodes_ids_v2] , node_ids )
        for node in nodes_ids_v1:
            self.assertEqual( len(node.get_coords())   , 3 )
            self.assertEqual( len(node.get_coords(-1)) , 3 )
            self.assertEqual( len(node.get_disp())     , 1 )
            self.assertEqual( len(node.get_vel())      , 1 ) 
            self.assertEqual( len(node.get_accel())    , 1 ) 
            self.assertGreater( len(node.get_elements()) , 0)

        node_indexes = [0,1]
        node_matching_ids = [1,2] # looked it up manually
        self.assertEqual( len(node_indexes) , len(node_matching_ids) )
        nodes_indexes_v1 = [d3plot.get_nodeByIndex(node_index) for node_index in node_indexes]
        nodes_indexes_v2 = d3plot.get_nodeByIndex(node_indexes)
        self.assertItemsEqual( [node.get_id() for node in nodes_indexes_v1] , node_matching_ids )
        self.assertItemsEqual( [node.get_id() for node in nodes_indexes_v2] , node_matching_ids )
        # .. TODO Error stoff
        
        ## Shell Element
        element_ids = [1,2]
        element_ids_shell_v1 = [d3plot.get_elementByID("shell", element_id) for element_id in element_ids]
        element_ids_shell_v2 = d3plot.get_elementByID("shell", element_ids)
        self.assertItemsEqual( [element.get_id() for element in element_ids_shell_v1] , element_ids )
        self.assertItemsEqual( [element.get_id() for element in element_ids_shell_v2] , element_ids )
        for element in element_ids_shell_v1:
            pass
        # .. TODO Error stoff
        


    def test_binout(self):
        """Testing all Binout functions"""

        binout_filepath = "test/binout"
        nTimesteps = 321
        content = ["swforc"] # TODO: special case rwforc
        content_subdirs = [['title', 'failure', 'ids', 'failure_time', 
                            'typenames', 'axial', 'version', 'shear', 'time', 'date', 
                            'length', 'resultant_moment', 'types', 'revision']]
        
        # open file
        binout = Binout(binout_filepath)

        # check directory stuff
        self.assertEqual( len(binout.read()) , len(content) )
        self.assertItemsEqual( content , binout.read() )

        # check variables reading
        for content_dir, content_subdirs in zip(content,content_subdirs):
            self.assertItemsEqual( content_subdirs , binout.read(content_dir) )
            self.assertEqual( nTimesteps , len(binout.read(content_dir,"time")) )

            for content_subdir in content_subdirs:
                # check if data containers not empty ... 
                self.assertGreater( len(binout.read(content_dir,content_subdir) ) , 0 ) 
        
        # check string conversion
        self.assertEqual( binout.to_string(binout.read("swforc","typenames")) ,
                          'constraint,weld,beam,solid,non nodal, ,solid assembly' )

        

if __name__ == "__main__":
    unittest.main()