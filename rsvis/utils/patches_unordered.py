# ===========================================================================
#   patches_unordered.py ------------------------------------------------------
# ===========================================================================

#   import ------------------------------------------------------------------
# ---------------------------------------------------------------------------
import rsvis.utils.patches

#   class -------------------------------------------------------------------
# ---------------------------------------------------------------------------
class UnorderedPatches(rsvis.utils.patches.Patches):

    #   method --------------------------------------------------------------
    # -----------------------------------------------------------------------
    def __init__(
        self, 
        img,
        **kwargs
    ):
        super(UnorderedPatches, self).__init__(img, **kwargs)
