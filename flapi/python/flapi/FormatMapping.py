from . import Library
import json

# FormatMapping
#
# Defines the mapping from one Format to another Format
#

class FormatMapping:
    
    # Constructor
    def __init__(self, obj=None):
        if obj != None:
            self.Sx = obj.get("Sx")
            self.Sy = obj.get("Sy")
            self.Tx = obj.get("Tx")
            self.Ty = obj.get("Ty")
            self.Inside = obj.get("Inside")
            self.SrcMask = obj.get("SrcMask")
            self.DstMask = obj.get("DstMask")
        else:
            self.Sx = None
            self.Sy = None
            self.Tx = None
            self.Ty = None
            self.Inside = None
            self.SrcMask = None
            self.DstMask = None

    @staticmethod
    def from_dict(o):
        return FormatMapping(o)

    def json(self):
        return {
            "_type": "FormatMapping",
            "Sx": self.Sx,
            "Sy": self.Sy,
            "Tx": self.Tx,
            "Ty": self.Ty,
            "Inside": self.Inside,
            "SrcMask": self.SrcMask,
            "DstMask": self.DstMask,
        }

    def __repr__(self):
        return "flapi.FormatMapping(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "FormatMapping", FormatMapping.from_dict );

