from pyDXHR.DRM import DRM
from pyDXHR.DRM.resolver import Reference


class ScenarioDRM(DRM):
    def open(self):
        super().open()

        unit_ref = Reference.from_root(self)

        ref_0 = unit_ref.deref(0)

        ref_2c = unit_ref.deref(0x2C)
        scn_name = ref_2c.deref(0).access_string()

        ref_30 = unit_ref.deref(0x30)

        # s_scn_det02_waynehaas_nonhostile_det_adam_apt_a
        # conv1 and 2 seem to be commentary tracks
        # conv1 = self.sections[41]
        # conv2 = self.sections[42]
        # conv3 = self.sections[43]
        #
        # conv3_ref = Reference.from_section(self, conv3)
        # conv_title = conv3_ref.deref(0x28).access_string()
        #
        # line1 = conv3_ref.deref(0x74).deref(0x0).access_string()
        # dtp_name_line1 = conv3_ref.deref(0x74).add(4).deref(0).access_string()
        # dtp_type_maybe = conv3_ref.deref(0x74).add(0xc).deref(0).access_string()

        # s_scn_det01_sq02_cassandra_end_det_adam_apt_a
        conv = self.sections[114]
        conv_ref = Reference.from_section(self, conv)
        conv_title = conv_ref.deref(0x28).access_string()
        line1 = conv_ref.deref(0x74).deref(0x0).access_string()
        dtp_name_line1 = conv_ref.deref(0x74).add(4).deref(0).access_string()
        dtp_type_maybe = conv_ref.deref(0x74).add(0xC).deref(0).access_string()

        breakpoint()
