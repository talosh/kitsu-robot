from . import Library, Interface, FLAPIException
import json

# Export
#
# Export operation
#

class Export(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a new Export operation object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Export): Export object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of Export" )
        return self.conn.call(
            None,
            "Export.create",
            {}
        )

    # select_all
    #
    # Select all snots in Scene to export
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def select_all(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.select_all",
            {}
        )

    # clear_selection
    #
    # Clear selection of shots in Scene to export
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def clear_selection(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.clear_selection",
            {}
        )

    # select_shots
    #
    # Set the selection to the given Shots for rendering
    #
    # Arguments:
    #    'shots' (list): Array of Shot objects to select
    #        '<n>' (Shot): 
    #
    # Returns:
    #    (none)
    #
    def select_shots(self, shots):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.select_shots",
            {
                'shots': shots,
            }
        )

    # select_shot
    #
    # Add the given shot to the selection to be exported.
    #
    # Arguments:
    #    'shot' (list): Shot to add to selection
    #        '<n>' (Shot): 
    #
    # Returns:
    #    (none)
    #
    def select_shot(self, shot):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.select_shot",
            {
                'shot': shot,
            }
        )

    # do_export_BLG
    #
    # Perform export BLG operation using the given Export settings
    #
    # Arguments:
    #    'queue' (QueueManager): QueueManager object for machine running render queue
    #    'scene' (Scene): Target scene to Export From
    #    'settings' (BLGExportSettings): 
    #
    # Returns:
    #    (ExportOpInfo): Operation info for job added to export queue
    #
    def do_export_BLG(self, queue, scene, settings):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.do_export_BLG",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        )

    # do_export_CDL
    #
    # Perform export CDL operation using the given Export settings
    #
    # Arguments:
    #    'queue' (QueueManager): QueueManager object for machine running render queue
    #    'scene' (Scene): Target scene to Export From
    #    'settings' (CDLExportSettings): 
    #
    # Returns:
    #    (ExportOpInfo): Operation info for job added to export queue
    #
    def do_export_CDL(self, queue, scene, settings):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.do_export_CDL",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        )

    # do_export_cube
    #
    # Perform export LUT operation using the given Export settings
    #
    # Arguments:
    #    'queue' (QueueManager): QueueManager object for machine running render queue
    #    'scene' (Scene): Target scene to Export From
    #    'settings' (CubeExportSettings): 
    #
    # Returns:
    #    (ExportOpInfo): Operation info for job added to export queue
    #
    def do_export_cube(self, queue, scene, settings):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.do_export_cube",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        )

    # do_export_still
    #
    # Perform export still operation using the given Export settings
    #
    # Arguments:
    #    'queue' (QueueManager): QueueManager object for machine running render queue
    #    'scene' (Scene): Target scene to Export From
    #    'settings' (StillExportSettings): 
    #
    # Returns:
    #    (ExportOpInfo): Operation info for job added to export queue
    #
    def do_export_still(self, queue, scene, settings):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.do_export_still",
            {
                'queue': queue,
                'scene': scene,
                'settings': settings,
            }
        )

    # get_log
    #
    # Return log of progress information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of Export progress information
    #        '<n>' (ExportProgress): 
    #
    def get_log(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Export.get_log",
            {}
        )

Library.register_class( 'Export', Export )

