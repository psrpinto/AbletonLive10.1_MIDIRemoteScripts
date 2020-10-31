# SVH Addition

from ableton.v2.control_surface.components import SessionRingComponent as Base


class SessionRingComponent(Base):
    """ SessionRingComponent that works with old framework and allows for dynamic width
    and height adjustments. """

    def __init__(self, *a, **k):
        # Components in the ableton framework do not have these methods, but
        # the old framework depends on them, so added no-ops here to satisfy
        fnc = lambda: None
        self.on_track_list_changed = fnc
        self.on_scene_list_changed = fnc
        self.on_selected_track_changed = fnc
        self.on_selected_scene_changed = fnc
        super(SessionRingComponent, self).__init__(*a, **k)
        self.set_offsets(
            0,
            0,
            width=self._session_ring.num_tracks,
            height=self._session_ring.num_scenes,
        )

    def set_offsets(self, track_offset, scene_offset, width=0, height=0):
        """ Extends standard to allow a width and height to be set. """
        self._session_ring.num_tracks = width if width else self._session_ring.num_tracks
        self._session_ring.num_scenes = height if height else self._session_ring.num_scenes
        super(SessionRingComponent, self).set_offsets(track_offset, scene_offset)
        # NOTE:  The touchAble app will need to receive a notification any time this
        # changes since it can be changed without using the app.
