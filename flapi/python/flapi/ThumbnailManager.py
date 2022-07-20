from . import Library, Interface, FLAPIException
import json

# ThumbnailManager
#
# Interface used to generate shot thumbnails
#

class ThumbnailManager(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_poster_uri
    #
    # Get a poster (or specific) frame thumbnail URI for a shot
    #
    # Arguments:
    #    'shot_if' (Shot): Shot interface object
    #    'graded' (int): Graded/ungraded flag
    #    'options' (dict): Stucture containing optional settings used to control the type of thumbnail image rendered.
    #        'DCSpace' (string): Display colourspace (sRGB or P3) [Optional]
    #        'HiRes' (string): Flag indicating hi-res image preferable [Optional]
    #        'ShotFrame' (int): Optional timeline frame number (constrained to shot range) [Optional]
    #
    # Returns:
    #    (string): Thumbnail URI
    #
    def get_poster_uri(self, shot_if, graded, options):
        if self.target != None:
            raise FLAPIException( "Static method get_poster_uri called on instance of ThumbnailManager" )
        return self.conn.call(
            None,
            "ThumbnailManager.get_poster_uri",
            {
                'shot_if': shot_if,
                'graded': graded,
                'options': options,
            }
        )

Library.register_class( 'ThumbnailManager', ThumbnailManager )

